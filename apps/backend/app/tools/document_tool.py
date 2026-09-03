"""
Document search tool for the agent.

Loads PDF and DOCX documents and searches for relevant paragraphs/pages
matching a query. All synchronous document parsing is wrapped in asyncio.to_thread().
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _search_pdf(file_path: str, query: str, max_results: int = 5) -> List[str]:
    """Search a PDF document for pages containing the query string."""
    import fitz

    query_lower = query.lower()
    results = []

    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        if query_lower in text.lower():
            # Return a context window around the match
            excerpt = text.strip()
            if len(excerpt) > 1000:
                idx = text.lower().find(query_lower)
                start = max(0, idx - 200)
                end = min(len(text), idx + len(query) + 200)
                excerpt = f"...{text[start:end].strip()}..."
            results.append(f"[Page {i + 1}] {excerpt}")
            if len(results) >= max_results:
                break
    doc.close()
    return results


def _search_docx(file_path: str, query: str, max_results: int = 5) -> List[str]:
    """Search a DOCX document for paragraphs containing the query string."""
    from docx import Document

    query_lower = query.lower()
    results = []

    doc = Document(file_path)
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text and query_lower in text.lower():
            results.append(f"[Paragraph {i + 1}] {text}")
            if len(results) >= max_results:
                break
    return results


def _search_text(file_path: str, query: str, max_results: int = 5) -> List[str]:
    """Search a plain text file for lines containing the query string."""
    query_lower = query.lower()
    results = []

    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if query_lower in line.lower():
                results.append(f"[Line {i}] {line.strip()}")
                if len(results) >= max_results:
                    break
    return results


async def search_document(
    file_path: str,
    query: str,
    max_results: int = 5,
) -> List[str]:
    """
    Search a document for content matching the query.

    Supports PDF, DOCX, and plain text files.
    All parsing runs in a thread pool to avoid blocking the event loop.

    Args:
        file_path: Path to the document file.
        query: Search query string.
        max_results: Maximum number of matching excerpts to return.

    Returns:
        List of matching excerpts with location context.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {file_path}")

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return await asyncio.to_thread(_search_pdf, file_path, query, max_results)
    elif suffix in (".docx", ".doc"):
        return await asyncio.to_thread(_search_docx, file_path, query, max_results)
    elif suffix in (".txt", ".md", ".csv", ".log"):
        return await asyncio.to_thread(_search_text, file_path, query, max_results)
    else:
        raise ValueError(f"Unsupported document format: {suffix}")


# Tool schema for agent tool calling
DOCUMENT_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_document",
        "description": "Search a document (PDF, DOCX, or text file) for content matching a query. Returns relevant excerpts with page/paragraph numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the document file to search.",
                },
                "query": {
                    "type": "string",
                    "description": "The search query to find within the document.",
                },
            },
            "required": ["file_path", "query"],
        },
    },
}
