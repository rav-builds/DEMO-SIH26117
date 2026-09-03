"""
Task intent router for Sovereign AI Workbench.

Analyzes TaskRequest parameters and intent to determine the appropriate execution pipeline.
"""

import logging
from typing import Optional
from app.schemas.tasks import TaskRequest, TaskType

logger = logging.getLogger(__name__)


class TaskRouter:
    """Routes incoming tasks to appropriate specialized engines or agent loops."""

    @staticmethod
    def route(task: TaskRequest) -> TaskType:
        """
        Determines the execution path.
        If task_type is explicitly specified (not GENERAL), honor it.
        If GENERAL, inspects prompt and file attachments for heuristics.
        """
        if task.task_type and task.task_type != TaskType.GENERAL:
            return task.task_type

        # Heuristic dispatch if set to GENERAL
        if task.sandbox_enabled:
            return TaskType.SANDBOX

        if task.file_paths:
            # Check file extensions
            first_ext = task.file_paths[0].lower().split(".")[-1]
            if first_ext in ("png", "jpg", "jpeg", "webp", "bmp", "tiff"):
                return TaskType.VISION
            if first_ext in ("pdf", "docx", "doc", "txt"):
                return TaskType.DOCUMENT

        prompt_lower = task.prompt.lower()
        if any(w in prompt_lower for w in ["search document", "search kb", "rag", "find in document"]):
            return TaskType.RAG

        if any(w in prompt_lower for w in ["calculate", "solve", "execute", "run code", "write a program", "plan and execute"]):
            return TaskType.AGENT

        return TaskType.GENERAL


task_router = TaskRouter()
