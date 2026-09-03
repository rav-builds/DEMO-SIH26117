"""
Tesseract OCR engine with PyMuPDF text extraction fallback.

All synchronous OCR and text extraction operations are wrapped in asyncio.to_thread()
to prevent blocking the FastAPI event loop.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _configure_tesseract() -> None:
    """Configure pytesseract with the system Tesseract binary path."""
    try:
        import pytesseract

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    except ImportError:
        logger.warning("pytesseract not installed; OCR will use fallback only.")


def _extract_text_tesseract(image_bytes: bytes, lang: str = "eng") -> str:
    """Extract text from image bytes using Tesseract OCR."""
    import pytesseract
    from PIL import Image
    import io

    _configure_tesseract()

    img = Image.open(io.BytesIO(image_bytes))

    # Convert to grayscale for better OCR accuracy
    if img.mode != "L":
        img = img.convert("L")

    text = pytesseract.image_to_string(img, lang=lang)
    return text.strip()


def _extract_text_pymupdf(file_path: str) -> str:
    """
    Fallback: extract text from a PDF or image file using PyMuPDF.
    Works without Tesseract for text-layer PDFs.
    """
    import fitz  # PyMuPDF

    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts).strip()


def _extract_text_from_pdf_page_image(file_path: str, page_num: int = 0, dpi: int = 200) -> str:
    """Render a PDF page to image, then OCR it with Tesseract (for scanned PDFs)."""
    import fitz
    import pytesseract
    from PIL import Image
    import io

    _configure_tesseract()

    doc = fitz.open(file_path)
    if page_num >= len(doc):
        doc.close()
        return ""

    page = doc[page_num]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)
    img_bytes = pix.tobytes("png")
    doc.close()

    img = Image.open(io.BytesIO(img_bytes))
    if img.mode != "L":
        img = img.convert("L")

    text = pytesseract.image_to_string(img)
    return text.strip()


# --------------------------------------------------------------------------
# Public async API
# --------------------------------------------------------------------------

async def ocr_image(image_bytes: bytes, lang: str = "eng") -> str:
    """
    Extract text from image bytes using Tesseract OCR.
    Falls back gracefully if Tesseract is not available.
    """
    try:
        return await asyncio.to_thread(_extract_text_tesseract, image_bytes, lang)
    except Exception as exc:
        logger.warning("Tesseract OCR failed: %s. No fallback for raw image bytes.", exc)
        return ""


async def ocr_document(file_path: str) -> str:
    """
    Extract text from a document file (PDF, image).
    Strategy:
    1. Try PyMuPDF text extraction (fast, works for text-layer PDFs)
    2. If result is empty/minimal, fall back to page-by-page Tesseract OCR
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {file_path}")

    suffix = path.suffix.lower()

    # For non-PDF images, go straight to Tesseract
    if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        image_bytes = await asyncio.to_thread(path.read_bytes)
        return await ocr_image(image_bytes)

    # For PDFs: try text extraction first, fall back to OCR
    if suffix == ".pdf":
        text = await asyncio.to_thread(_extract_text_pymupdf, file_path)
        if text and len(text.split()) > 10:
            return text

        # Scanned PDF — OCR each page
        logger.info("PDF text extraction yielded minimal results; falling back to OCR for %s", file_path)
        try:
            import fitz
            doc = await asyncio.to_thread(fitz.open, file_path)
            page_count = len(doc)
            doc.close()

            pages = []
            for i in range(page_count):
                page_text = await asyncio.to_thread(
                    _extract_text_from_pdf_page_image, file_path, i
                )
                if page_text:
                    pages.append(page_text)
            return "\n\n".join(pages)
        except Exception as exc:
            logger.error("OCR fallback failed for %s: %s", file_path, exc)
            return text  # Return whatever text extraction got

    raise ValueError(f"Unsupported file type for OCR: {suffix}")
