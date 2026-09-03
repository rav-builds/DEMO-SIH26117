from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskType(str, Enum):
    GENERAL = "general"
    RAG = "rag"
    AGENT = "agent"
    VISION = "vision"
    DOCUMENT = "document"
    SANDBOX = "sandbox"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


# Maximum number of keys allowed in arbitrary dict fields to prevent memory exhaustion
_MAX_DICT_KEYS = 50
_MAX_FILE_PATHS = 20


class TaskRequest(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=50_000,
        description="Prompt or primary instruction for the task (max 50,000 characters)",
        examples=["Analyze the uploaded financial report and highlight risk factors."]
    )
    task_type: TaskType = Field(
        default=TaskType.GENERAL,
        description="Type of task to dispatch",
        examples=[TaskType.GENERAL]
    )
    model: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Specific model override to execute the task (e.g. 'ornith-1.5:9b-q4_k_m')",
        examples=["ornith-1.5:9b-q4_k_m"]
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature for generation"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        max_length=10_000,
        description="Custom system prompt override"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Arbitrary context data, document metadata, or conversational history"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution or tool-specific parameters"
    )
    file_paths: List[str] = Field(
        default_factory=list,
        max_length=_MAX_FILE_PATHS,
        description=f"Referenced file paths or ingested document identifiers (max {_MAX_FILE_PATHS})"
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream real-time events and tokens"
    )
    sandbox_enabled: bool = Field(
        default=False,
        description="Whether to execute generated code in isolated sandbox"
    )
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL,
        description="Queue priority level"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="User or caller provided metadata"
    )

    @field_validator("context", mode="before")
    @classmethod
    def _cap_context_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is not None and isinstance(v, dict) and len(v) > _MAX_DICT_KEYS:
            raise ValueError(f"context dict exceeds maximum of {_MAX_DICT_KEYS} keys")
        return v

    @field_validator("parameters", mode="before")
    @classmethod
    def _cap_parameters_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(v, dict) and len(v) > _MAX_DICT_KEYS:
            raise ValueError(f"parameters dict exceeds maximum of {_MAX_DICT_KEYS} keys")
        return v

    @field_validator("metadata", mode="before")
    @classmethod
    def _cap_metadata_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(v, dict) and len(v) > _MAX_DICT_KEYS:
            raise ValueError(f"metadata dict exceeds maximum of {_MAX_DICT_KEYS} keys")
        return v


# Alias for compatibility with common controller conventions
TaskCreate = TaskRequest


class TaskResult(BaseModel):
    output: Any = Field(..., description="Primary output or response payload")
    artifacts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated artifacts (charts, code files, exports)"
    )
    model_used: Optional[str] = Field(
        default=None,
        description="Model actually used to fulfill the task"
    )
    token_usage: Optional[Dict[str, int]] = Field(
        default=None,
        description="Token consumption metrics: prompt_tokens, completion_tokens, total_tokens"
    )
    execution_time_seconds: Optional[float] = Field(
        default=None,
        description="Total duration of execution in seconds"
    )
    logs: Optional[List[str]] = Field(
        default=None,
        description="Execution trace or diagnostic log lines"
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    task_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the task"
    )
    task_type: TaskType = Field(..., description="Type of task")
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current execution status"
    )
    prompt: str = Field(..., description="Original input prompt")
    result: Optional[Any] = Field(
        default=None,
        description="Task result payload if completed"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error explanation if status is failed"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when task was created (UTC)"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when task completed or failed (UTC)"
    )
    execution_time_seconds: Optional[float] = Field(
        default=None,
        description="Elapsed execution time in seconds"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Associated execution metadata"
    )


class TaskStatusResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current status of the task")
    progress: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Completion progress between 0.0 and 1.0"
    )
    message: Optional[str] = Field(
        default=None,
        description="Human-readable progress or status description"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Task creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last status update timestamp"
    )


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse] = Field(default_factory=list)
    total: int = Field(default=0, description="Total number of tasks")


class TaskCancelResponse(BaseModel):
    task_id: str = Field(..., description="Target task ID")
    status: TaskStatus = Field(default=TaskStatus.CANCELLED)
    message: str = Field(default="Task execution cancelled successfully")
