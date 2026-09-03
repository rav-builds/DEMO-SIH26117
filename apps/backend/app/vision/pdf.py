"""
PyMuPDF document renderer and parser.

Extracts text, metadata, and page images from PDF documents.
All synchronous PyMuPDF calls are wrapped in asyncio.to_thread().
"""

import asyncio
import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Synchronous helpers (run inside thread pool)
# --------------------------------------------------------------------------

def _extract_text_by_page(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from each page of a PDF document."""
    import fitz

    doc = fitz.open(file_path)
    pages = []
    for i, page in enumerate(doc):
        pages.append({
            "page_number": i + 1,
            "text": page.get_text().strip(),
            "width": page.rect.width,
            "height": page.rect.height,
        })
    doc.close()
    return pages


def _extract_full_text(file_path: str) -> str:
    """Extract all text from a PDF as a single string."""
    import fitz

    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts).strip()


def _extract_metadata(file_path: str) -> Dict[str, Any]:
    """Extract PDF metadata (title, author, page count, etc.)."""
    import fitz

    doc = fitz.open(file_path)
    meta = doc.metadata or {}
    info = {
        "title": meta.get("title", ""),
        "author": meta.get("author", ""),
        "subject": meta.get("subject", ""),
        "creator": meta.get("creator", ""),
        "producer": meta.get("producer", ""),
        "page_count": len(doc),
        "file_path": file_path,
    }
    doc.close()
    return info


def _render_page_to_image(file_path: str, page_num: int = 0, dpi: int = 200) -> bytes:
    """Render a specific PDF page to PNG image bytes."""
    import fitz

    doc = fitz.open(file_path)
    if page_num >= len(doc):
        doc.close()
        raise IndexError(f"Page {page_num} does not exist (document has {len(doc)} pages)")

    page = doc[page_num]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def _render_all_pages_to_images(file_path: str, dpi: int = 150) -> List[bytes]:
    """Render all pages of a PDF to PNG image bytes."""
    import fitz

    doc = fitz.open(file_path)
    images = []
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        images.append(pix.tobytes("png"))
    doc.close()
    return images


# --------------------------------------------------------------------------
# Public async API
# --------------------------------------------------------------------------

async def extract_text_by_page(file_path: str) -> List[Dict[str, Any]]:
    """Extract text from each page of a PDF (async, non-blocking)."""
    _validate_pdf(file_path)
    return await asyncio.to_thread(_extract_text_by_page, file_path)


async def extract_full_text(file_path: str) -> str:
    """Extract all text from a PDF as a single string (async, non-blocking)."""
    _validate_pdf(file_path)
    return await asyncio.to_thread(_extract_full_text, file_path)


async def extract_metadata(file_path: str) -> Dict[str, Any]:
    """Extract PDF metadata (async, non-blocking)."""
    _validate_pdf(file_path)
    return await asyncio.to_thread(_extract_metadata, file_path)


async def render_page_to_image(file_path: str, page_num: int = 0, dpi: int = 200) -> bytes:
    """Render a PDF page to PNG image bytes (async, non-blocking)."""
    _validate_pdf(file_path)
    return await asyncio.to_thread(_render_page_to_image, file_path, page_num, dpi)


async def render_all_pages_to_images(file_path: str, dpi: int = 150) -> List[bytes]:
    """Render all PDF pages to PNG image bytes (async, non-blocking)."""
    _validate_pdf(file_path)
    return await asyncio.to_thread(_render_all_pages_to_images, file_path, dpi)


def _validate_pdf(file_path: str) -> None:
    """Validate that the file exists and is a PDF."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected PDF file, got: {path.suffix}")
