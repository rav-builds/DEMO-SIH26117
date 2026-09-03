from typing import List, Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings loaded from environment variables and .env files.
    Ensures model endpoints, security keys, and serving toggles are strictly externalized.
    """

    # Application Information
    app_name: str = "Sovereign AI Workbench"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Model Serving Backend Toggle ('ollama' | 'mlx' | 'vllm')
    model_backend: Literal["ollama", "mlx", "vllm"] = Field(
        default="ollama",
        validation_alias="MODEL_BACKEND"
    )
    serving_backend: Optional[Literal["ollama", "mlx", "vllm"]] = Field(
        default=None,
        validation_alias="SERVING_BACKEND"
    )

    # 1. Ollama Backend Settings (CPU/GGUF Fallback)
    ollama_base_url: str = "http://localhost:11434"
    ollama_openai_url: str = "http://localhost:11434/v1"
    ollama_timeout_seconds: float = 120.0
    ollama_model: str = "ornith-1.5:9b-q4_k_m"

    # 2. MLX Backend Settings (Apple Silicon via LM Studio or mlx_lm.server)
    mlx_base_url: str = "http://localhost:1234/v1"
    mlx_timeout_seconds: float = 120.0
    mlx_model: str = "ornith-ai/Ornith-1.5-9B-MLX"

    # 3. vLLM Backend Settings (GPU Server)
    vllm_base_url: str = "http://localhost:8000/v1"
    vllm_timeout_seconds: float = 120.0
    vllm_model: str = "ornith-ai/Ornith-1.5-9B"

    # Role Model Defaults
    default_coding_model: str = "ornith-1.5:9b-q4_k_m"
    default_vision_model: str = "ornith-1.5:9b-q4_k_m"
    default_embedding_model: str = "nomic-embed-text"

    # Qdrant Vector Store
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "sovereign_knowledge_base"
    embedding_dimension: int = 768

    # Vision & OCR Settings
    tesseract_cmd: Optional[str] = None

    # Sandbox & Security Limits
    sandbox_timeout_seconds: int = 30
    sandbox_max_memory_mb: int = 256
    sandbox_network_access: bool = False
    secret_key: str = "insecure-default-change-me-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # File-backed persistence paths
    audit_log_path: str = "data/audit.jsonl"
    task_store_path: str = "data/tasks.jsonl"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def active_backend(self) -> str:
        """Resolves active backend from MODEL_BACKEND or fallback SERVING_BACKEND."""
        return self.serving_backend or self.model_backend

    @property
    def active_model_endpoint(self) -> str:
        """Returns the OpenAI-compatible endpoint URL for the selected backend."""
        backend = self.active_backend
        if backend == "vllm":
            return self.vllm_base_url
        elif backend == "mlx":
            return self.mlx_base_url
        return self.ollama_openai_url

    @property
    def active_model_name(self) -> str:
        """Returns the primary model identifier for the selected backend."""
        backend = self.active_backend
        if backend == "vllm":
            return self.vllm_model
        elif backend == "mlx":
            return self.mlx_model
        return self.ollama_model

    @property
    def active_timeout_seconds(self) -> float:
        """Returns the request timeout in seconds."""
        backend = self.active_backend
        if backend == "vllm":
            return self.vllm_timeout_seconds
        elif backend == "mlx":
            return self.mlx_timeout_seconds
        return self.ollama_timeout_seconds

    @property
    def parsed_allowed_origins(self) -> List[str]:
        """Parses comma-separated allowed origins into a clean list for CORS middleware."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
