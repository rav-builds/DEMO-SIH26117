from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message author role: system, user, assistant, or tool")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Text content or multimodal content parts")
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class GenerationRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = 4096
    top_p: Optional[float] = 0.9
    stream: bool = False
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    extra_body: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    content: str = ""
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finish_reason: Optional[str] = None
    model: str = ""
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseModelClient(ABC):
    """Abstract interface defining the model-agnostic contract for local and remote LLMs."""

    @abstractmethod
    async def chat(self, request: GenerationRequest) -> GenerationResponse:
        """Send a chat completion request and return a structured response."""
        pass

    @abstractmethod
    async def stream_chat(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Stream response tokens or text chunks asynchronously."""
        pass

    @abstractmethod
    async def embeddings(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the underlying serving backend is reachable and responsive."""
        pass
