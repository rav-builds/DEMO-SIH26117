import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from app.config import settings
from app.models.base import BaseModelClient
from app.models.local_client import LocalClient

logger = logging.getLogger(__name__)


class ModelRegistry:
    """
    Central registry for local model management, role routing, and client dispatch.
    Decouples application agents and pipelines from the physical model serving backend.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_path()
        self._config_cache: Dict[str, Any] = {}
        self._client_cache: Dict[str, LocalClient] = {}
        self._load_config()

    def _find_config_path(self) -> str:
        """Walks up the directory tree to locate configs/models.yaml reliably."""
        current = Path(__file__).resolve().parent
        for parent in [current, *current.parents]:
            candidate = parent / "configs" / "models.yaml"
            if candidate.is_file():
                return str(candidate)

        # Standard fallback relative paths
        fallbacks = [
            Path("configs/models.yaml"),
            Path("../configs/models.yaml"),
            Path("../../configs/models.yaml"),
        ]
        for fb in fallbacks:
            if fb.is_file():
                return str(fb.resolve())

        logger.warning("Could not find configs/models.yaml in parent paths; using fallback.")
        return "configs/models.yaml"

    def _load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config_cache = yaml.safe_load(f) or {}
            except Exception as exc:
                logger.error("Failed to parse %s: %s", self.config_path, exc)
                self._config_cache = {}

    def reload(self) -> None:
        """Reload configuration from disk and reset client instances."""
        self._load_config()
        self._client_cache.clear()

    @property
    def active_backend(self) -> str:
        return settings.active_backend

    def get_backend_config(self, backend: Optional[str] = None) -> Dict[str, Any]:
        target = backend or self.active_backend
        backends = self._config_cache.get("serving_backends", {})
        return backends.get(target, {})

    def get_model_id(self, role: str = "reasoning") -> str:
        """Resolves the default model identifier for the given role and active backend."""
        backend = self.active_backend
        if role == "embedding":
            return settings.default_embedding_model

        if role == "coding":
            return settings.vllm_model if backend == "vllm" else settings.default_coding_model
        elif role == "vision":
            return settings.vllm_model if backend == "vllm" else settings.default_vision_model

        # Default reasoning role
        if backend == "vllm":
            return settings.vllm_model
        elif backend == "mlx":
            return settings.mlx_model
        else:
            return settings.ollama_model

    def get_client(self, role: str = "reasoning", model_id: Optional[str] = None) -> BaseModelClient:
        """
        Returns a cached or newly initialized LocalClient for the requested role or model ID.
        """
        selected_model = model_id or self.get_model_id(role)
        cache_key = f"{settings.active_model_endpoint}:{selected_model}"

        if cache_key not in self._client_cache:
            self._client_cache[cache_key] = LocalClient(
                base_url=settings.active_model_endpoint,
                default_model=selected_model,
                timeout=settings.active_timeout_seconds,
            )
        return self._client_cache[cache_key]

    async def aclose(self) -> None:
        """Closes all cached client HTTP sessions."""
        for client in self._client_cache.values():
            await client.aclose()
        self._client_cache.clear()

    def list_models_for_role(self, role: str) -> List[Dict[str, Any]]:
        models_catalog = self._config_cache.get("models", {})
        return models_catalog.get(role, [])

    def get_serving_command(self, backend: Optional[str] = None) -> str:
        target = backend or self.active_backend
        backend_cfg = self.get_backend_config(target)
        return backend_cfg.get("launch_command", backend_cfg.get("launch_command_cli", ""))


# Singleton registry instance
model_registry = ModelRegistry()
