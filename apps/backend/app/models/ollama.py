import logging
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings
from app.models.local_client import LocalClient

logger = logging.getLogger(__name__)


class OllamaClient(LocalClient):
    """
    Ollama-specific client with support for native Ollama lifecycle methods (tags, pull)
    while inheriting the standard OpenAI-compatible chat and embedding execution.

    Maintains a separate persistent HTTP client for native Ollama API calls (/api/tags,
    /api/pull) to avoid socket leaks from repeatedly creating temporary clients.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        raw_base = (base_url or settings.ollama_base_url).rstrip("/")
        # If passed base_url ends in /v1, set native base appropriately
        if raw_base.endswith("/v1"):
            self.native_base_url = raw_base[:-3]
            openai_base = raw_base
        else:
            self.native_base_url = raw_base
            openai_base = f"{raw_base}/v1"

        super().__init__(
            base_url=openai_base,
            default_model=default_model or settings.ollama_model,
            timeout=timeout or settings.ollama_timeout_seconds,
        )

        # Persistent client for native Ollama API (non-OpenAI endpoints).
        # Uses a generous timeout for model pull operations (up to 10 minutes).
        self._native_client = httpx.AsyncClient(
            timeout=600.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def aclose(self) -> None:
        """Closes both the OpenAI-compatible and native Ollama HTTP pools."""
        await super().aclose()
        if not self._native_client.is_closed:
            await self._native_client.aclose()

    async def list_local_models(self) -> List[Dict[str, Any]]:
        """Query native Ollama /api/tags for installed models."""
        endpoint = f"{self.native_base_url}/api/tags"
        try:
            res = await self._native_client.get(endpoint, timeout=10.0)
            res.raise_for_status()
            data = res.json()
            return data.get("models", [])
        except Exception as exc:
            logger.debug("Failed to list Ollama models at %s: %s", endpoint, exc)
            return []

    async def pull_model(self, model_name: str) -> bool:
        """Trigger model download in Ollama."""
        endpoint = f"{self.native_base_url}/api/pull"
        try:
            res = await self._native_client.post(
                endpoint, json={"name": model_name, "stream": False}
            )
            return res.status_code == 200
        except Exception as exc:
            logger.error("Failed to pull model '%s' from %s: %s", model_name, endpoint, exc)
            return False
