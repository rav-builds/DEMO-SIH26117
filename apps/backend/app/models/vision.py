import base64
import io
import logging
from typing import Any, Dict, List, Optional

from PIL import Image

from app.config import settings
from app.models.base import ChatMessage, GenerationRequest, GenerationResponse
from app.models.local_client import LocalClient

logger = logging.getLogger(__name__)

# Maximum dimension (width or height) before downscaling
_MAX_IMAGE_DIMENSION = 1024
_JPEG_QUALITY = 75


class VisionClient:
    """
    Multimodal vision client supporting models with vision projectors (e.g. Ornith-1.5-9B with mmproj, LLaVA).
    Encodes images into OpenAI-compatible base64 payload blocks.

    Automatically optimizes images before encoding:
    - Resizes to max 1024px on longest edge (maintaining aspect ratio)
    - Converts to RGB (strips alpha channel)
    - Compresses to JPEG quality=75
    """

    def __init__(self, client: Optional[LocalClient] = None, model: Optional[str] = None):
        self.client = client or LocalClient(
            base_url=settings.active_model_endpoint,
            default_model=model or (settings.vllm_model if settings.serving_backend == "vllm" else settings.default_vision_model),
            timeout=settings.active_timeout_seconds,
        )
        self.model = model or self.client.default_model

    @staticmethod
    def optimize_image(
        image_bytes: bytes,
        max_dimension: int = _MAX_IMAGE_DIMENSION,
        quality: int = _JPEG_QUALITY,
    ) -> tuple[bytes, str]:
        """
        Resize and compress image bytes using Pillow.

        Returns:
            Tuple of (optimized_bytes, mime_type). Always returns JPEG.
        """
        img = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary (strips alpha, handles palette modes)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Resize to fit within max_dimension, preserving aspect ratio
        width, height = img.size
        if max(width, height) > max_dimension:
            ratio = max_dimension / max(width, height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            logger.debug(
                "Resized image from %dx%d to %dx%d", width, height, new_width, new_height
            )

        # Compress to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        optimized = buffer.getvalue()

        logger.debug(
            "Image optimized: %d bytes -> %d bytes (%.0f%% reduction)",
            len(image_bytes),
            len(optimized),
            (1 - len(optimized) / max(len(image_bytes), 1)) * 100,
        )

        return optimized, "image/jpeg"

    @staticmethod
    def encode_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """Encodes raw image bytes into a data URI."""
        b64_str = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{b64_str}"

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        mime_type: str = "image/jpeg",
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        optimize: bool = True,
    ) -> GenerationResponse:
        """
        Analyze an image using the multimodal vision model.

        Args:
            image_bytes: Raw image bytes.
            prompt: Analysis instruction.
            mime_type: Original MIME type (overridden to image/jpeg if optimized).
            system_prompt: Optional system prompt.
            temperature: Sampling temperature (low for precision).
            optimize: Whether to resize/compress before encoding (default True).
        """
        if optimize:
            image_bytes, mime_type = self.optimize_image(image_bytes)

        data_uri = self.encode_image(image_bytes, mime_type)

        content_parts: List[Dict[str, Any]] = [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": data_uri,
                },
            },
        ]

        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        messages.append(ChatMessage(role="user", content=content_parts))

        request = GenerationRequest(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )

        return await self.client.chat(request)
