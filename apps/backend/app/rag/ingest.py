"""
Document ingestion pipeline for the RAG system.

Parses documents (PDF, DOCX, TXT), chunks text using a recursive character
splitter, generates embeddings via the batched EmbeddingService, and upserts
into the Qdrant vector store.

All synchronous document parsing is wrapped in asyncio.to_thread().
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store

logger = logging.getLogger(__name__)

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64


class IngestResult(BaseModel):
    """Result of a document ingestion operation."""

    source: str = Field(..., description="Source file path or identifier")
    total_chunks: int = Field(default=0, description="Number of chunks created")
    total_characters: int = Field(default=0, description="Total characters ingested")
    success: bool = Field(default=True)
    error: Optional[str] = Field(default=None)


# --------------------------------------------------------------------------
# Synchronous document parsers (run inside thread pool)
# --------------------------------------------------------------------------

def _parse_pdf(file_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    import fitz

    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts)


def _parse_docx(file_path: str) -> str:
    """Extract all text from a DOCX file using python-docx."""
    from docx import Document

    doc = Document(file_path)
    return "\n\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )


def _parse_text(file_path: str) -> str:
    """Read a plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


# --------------------------------------------------------------------------
# Text chunking
# --------------------------------------------------------------------------

def _chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    """
    Split text into overlapping chunks using a recursive character splitter.

    Tries to split on paragraph boundaries (\n\n), then sentence boundaries (.),
    then word boundaries (space), and finally character-level as a last resort.
    """
    if not text or not text.strip():
        return []

    separators = ["\n\n", "\n", ". ", " ", ""]
    chunks: List[str] = []
    _recursive_split(text.strip(), separators, chunk_size, chunk_overlap, chunks)
    return chunks


def _recursive_split(
    text: str,
    separators: List[str],
    chunk_size: int,
    chunk_overlap: int,
    result: List[str],
) -> None:
    """Recursively split text using a hierarchy of separators."""
    if len(text) <= chunk_size:
        if text.strip():
            result.append(text.strip())
        return

    separator = separators[0] if separators else ""
    remaining_separators = separators[1:] if len(separators) > 1 else [""]

    if separator:
        parts = text.split(separator)
    else:
        # Character-level split as last resort
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk = text[i: i + chunk_size].strip()
            if chunk:
                result.append(chunk)
        return

    current_chunk = ""
    for part in parts:
        candidate = f"{current_chunk}{separator}{part}" if current_chunk else part

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk.strip():
                result.append(current_chunk.strip())
            # If single part is too large, recursively split it
            if len(part) > chunk_size:
                _recursive_split(part, remaining_separators, chunk_size, chunk_overlap, result)
                current_chunk = ""
            else:
                # Start new chunk with overlap from previous
                if current_chunk and chunk_overlap > 0:
                    overlap_text = current_chunk[-chunk_overlap:]
                    current_chunk = overlap_text + separator + part
                else:
                    current_chunk = part

    if current_chunk.strip():
        result.append(current_chunk.strip())


# --------------------------------------------------------------------------
# Public async API
# --------------------------------------------------------------------------

async def ingest_file(
    file_path: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    source_id: Optional[str] = None,
) -> IngestResult:
    """
    Ingest a document into the RAG knowledge base.

    Pipeline:
    1. Parse document (PDF, DOCX, TXT) in a thread pool
    2. Chunk text with recursive character splitter
    3. Generate embeddings via batched EmbeddingService
    4. Upsert chunks + vectors into Qdrant

    Args:
        file_path: Path to the document file.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between adjacent chunks.
        source_id: Optional identifier for the source (defaults to filename).

    Returns:
        IngestResult with ingestion statistics.
    """
    path = Path(file_path)
    source = source_id or path.name

    if not path.is_file():
        return IngestResult(source=source, success=False, error=f"File not found: {file_path}")

    suffix = path.suffix.lower()

    # Step 1: Parse document (non-blocking)
    try:
        if suffix == ".pdf":
            raw_text = await asyncio.to_thread(_parse_pdf, file_path)
        elif suffix in (".docx", ".doc"):
            raw_text = await asyncio.to_thread(_parse_docx, file_path)
        elif suffix in (".txt", ".md", ".csv"):
            raw_text = await asyncio.to_thread(_parse_text, file_path)
        else:
            return IngestResult(
                source=source, success=False,
                error=f"Unsupported file type: {suffix}",
            )
    except Exception as exc:
        logger.error("Failed to parse %s: %s", file_path, exc)
        return IngestResult(source=source, success=False, error=str(exc))

    if not raw_text.strip():
        return IngestResult(
            source=source, success=False, error="Document contains no extractable text"
        )

    # Step 2: Chunk text
    chunks_text = _chunk_text(raw_text, chunk_size, chunk_overlap)
    if not chunks_text:
        return IngestResult(source=source, success=False, error="No chunks produced")

    logger.info("Document '%s': %d characters → %d chunks", source, len(raw_text), len(chunks_text))

    # Step 3: Generate embeddings (batched)
    try:
        vectors = await embedding_service.embed_texts(chunks_text)
    except Exception as exc:
        logger.error("Embedding generation failed for '%s': %s", source, exc)
        return IngestResult(source=source, success=False, error=f"Embedding failed: {exc}")

    # Step 4: Upsert into Qdrant
    try:
        vector_store.ensure_collection()

        chunk_dicts = [
            {
                "text": text,
                "source": source,
                "chunk_index": i,
                "file_path": str(path),
            }
            for i, text in enumerate(chunks_text)
        ]

        vector_store.upsert(chunk_dicts, vectors)
    except Exception as exc:
        logger.error("Vector store upsert failed for '%s': %s", source, exc)
        return IngestResult(source=source, success=False, error=f"Upsert failed: {exc}")

    return IngestResult(
        source=source,
        total_chunks=len(chunks_text),
        total_characters=len(raw_text),
        success=True,
    )


async def delete_source(source_id: str) -> None:
    """Delete all chunks for a given source from the vector store."""
    try:
        vector_store.delete_by_source(source_id)
        logger.info("Deleted source '%s' from knowledge base", source_id)
    except Exception as exc:
        logger.error("Failed to delete source '%s': %s", source_id, exc)
        raise
