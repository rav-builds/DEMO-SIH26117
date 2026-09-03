"""
Streaming event schemas for Server-Sent Events (SSE).

Defines structured event models that can be streamed to the client during
task execution, agent reasoning, and token generation.
"""

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class StreamEventType(str, Enum):
    TOKEN = "token"
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    STATUS = "status"
    COMPLETION = "completion"
    ERROR = "error"


class StreamEvent(BaseModel):
    """Base streaming event structure serializable to SSE."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: StreamEventType = Field(default=StreamEventType.TOKEN)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    task_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)

    def to_sse(self) -> str:
        """Serialize into SSE format `event: ...\ndata: ...\n\n`."""
        payload = {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            **self.data,
        }
        return f"event: {self.event_type.value}\ndata: {json.dumps(payload)}\n\n"


class TokenEvent(StreamEvent):
    """Event emitted for individual generated tokens."""
    def __init__(self, token: str, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.TOKEN,
            task_id=task_id,
            data={"token": token},
            **kwargs,
        )


class ReasoningEvent(StreamEvent):
    """Event emitted for thinking / reasoning trace tokens (<think> blocks)."""
    def __init__(self, reasoning: str, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.REASONING,
            task_id=task_id,
            data={"reasoning": reasoning},
            **kwargs,
        )


class ToolCallEvent(StreamEvent):
    """Event emitted when the agent invokes an external tool."""
    def __init__(self, tool_name: str, tool_input: Dict[str, Any], task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.TOOL_CALL,
            task_id=task_id,
            data={"tool_name": tool_name, "tool_input": tool_input},
            **kwargs,
        )


class ToolResultEvent(StreamEvent):
    """Event emitted when a tool completes execution."""
    def __init__(self, tool_name: str, result: Any, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.TOOL_RESULT,
            task_id=task_id,
            data={"tool_name": tool_name, "result": result},
            **kwargs,
        )


class StatusEvent(StreamEvent):
    """Event emitted for status / progress updates."""
    def __init__(self, status: str, message: Optional[str] = None, progress: Optional[float] = None, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.STATUS,
            task_id=task_id,
            data={"status": status, "message": message, "progress": progress},
            **kwargs,
        )


class CompletionEvent(StreamEvent):
    """Event emitted upon task completion with full result."""
    def __init__(self, result: Any, execution_time_seconds: Optional[float] = None, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.COMPLETION,
            task_id=task_id,
            data={"result": result, "execution_time_seconds": execution_time_seconds},
            **kwargs,
        )


class ErrorEvent(StreamEvent):
    """Event emitted when an error occurs."""
    def __init__(self, error: str, task_id: Optional[str] = None, **kwargs: Any):
        super().__init__(
            event_type=StreamEventType.ERROR,
            task_id=task_id,
            data={"error": error},
            **kwargs,
        )
