"""
Agent execution state schemas and models.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from app.models.base import ChatMessage


class AgentStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class StepResult(BaseModel):
    """Result of a single step taken by the agent."""
    step_index: int
    thinking: Optional[str] = None
    action: Optional[str] = None
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    error: Optional[str] = None


class AgentState(BaseModel):
    """Mutable state maintained during an autonomous agent run."""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str = ""
    messages: List[ChatMessage] = Field(default_factory=list)
    current_step: int = 0
    max_steps: int = 10
    status: AgentStatus = AgentStatus.IDLE
    reasoning_trace: List[str] = Field(default_factory=list)
    step_results: List[StepResult] = Field(default_factory=list)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    final_output: Optional[str] = None
    error: Optional[str] = None

    def add_step_result(self, step: StepResult) -> None:
        self.step_results.append(step)
        self.current_step += 1
        if step.thinking:
            self.reasoning_trace.append(step.thinking)
        if step.tool_name and step.tool_output is not None:
            self.tool_results[f"{step.tool_name}_{self.current_step}"] = step.tool_output
