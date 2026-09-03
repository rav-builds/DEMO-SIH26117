"""
Image preprocessing utilities for the vision pipeline.

Provides async-safe image operations using Pillow, wrapped in asyncio.to_thread()
to avoid blocking the FastAPI event loop.
"""

import asyncio
import io
import logging
from typing import Optional, Tuple

from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


def _resize_image(
    image_bytes: bytes,
    max_dimension: int = 1024,
) -> bytes:
    """Resize image to fit within max_dimension, preserving aspect ratio."""
    img = Image.open(io.BytesIO(image_bytes))

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    width, height = img.size
    if max(width, height) > max_dimension:
        ratio = max_dimension / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    return buffer.getvalue()


def _enhance_for_ocr(image_bytes: bytes) -> bytes:
    """
    Enhance image for better OCR accuracy:
    - Convert to grayscale
    - Increase contrast
    - Sharpen edges
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to grayscale for OCR
    img = img.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def _get_image_info(image_bytes: bytes) -> dict:
    """Extract image metadata: dimensions, mode, format."""
    img = Image.open(io.BytesIO(image_bytes))
    return {
        "width": img.size[0],
        "height": img.size[1],
        "mode": img.mode,
        "format": img.format or "unknown",
        "size_bytes": len(image_bytes),
    }


def _convert_color_space(
    image_bytes: bytes,
    target_mode: str = "RGB",
) -> bytes:
    """Convert image to a target color space (RGB, L, RGBA)."""
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode != target_mode:
        img = img.convert(target_mode)

    fmt = "PNG" if target_mode == "RGBA" else "JPEG"
    buffer = io.BytesIO()
    img.save(buffer, format=fmt, quality=85 if fmt == "JPEG" else None)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# Async wrappers — safe for use inside FastAPI route handlers
# --------------------------------------------------------------------------

async def resize_image(image_bytes: bytes, max_dimension: int = 1024) -> bytes:
    """Async wrapper for image resizing (runs in thread pool)."""
    return await asyncio.to_thread(_resize_image, image_bytes, max_dimension)


async def enhance_for_ocr(image_bytes: bytes) -> bytes:
    """Async wrapper for OCR image enhancement (runs in thread pool)."""
    return await asyncio.to_thread(_enhance_for_ocr, image_bytes)


async def get_image_info(image_bytes: bytes) -> dict:
    """Async wrapper for image metadata extraction (runs in thread pool)."""
    return await asyncio.to_thread(_get_image_info, image_bytes)


async def convert_color_space(image_bytes: bytes, target_mode: str = "RGB") -> bytes:
    """Async wrapper for color space conversion (runs in thread pool)."""
    return await asyncio.to_thread(_convert_color_space, image_bytes, target_mode)
