"""
Task management and execution API routes.

Supports:
- POST /api/tasks (dispatch background task or synchronous processing)
- GET /api/tasks (list recent tasks)
- GET /api/tasks/{task_id} (fetch task status and output)
- DELETE /api/tasks/{task_id} (cancel running task)
- GET /api/tasks/{task_id}/stream (SSE token and reasoning stream)
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

import aiofiles
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.agent.graph import agent_graph
from app.agent.router import task_router
from app.agent.state import AgentState
from app.config import settings
from app.models.base import ChatMessage, GenerationRequest
from app.models.registry import model_registry
from app.models.vision import VisionClient
from app.rag.retriever import hybrid_retriever
from app.sandbox.docker_runner import DockerSandboxRunner
from app.schemas.events import CompletionEvent, ErrorEvent, ReasoningEvent, StatusEvent, TokenEvent
from app.schemas.response import APIResponse
from app.schemas.tasks import (
    TaskCancelResponse,
    TaskListResponse,
    TaskPriority,
    TaskRequest,
    TaskResponse,
    TaskResult,
    TaskStatus,
    TaskStatusResponse,
    TaskType,
)
from app.security.audit import audit_logger

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks")

# In-memory fast cache and persistence file path
_tasks_cache: Dict[str, TaskResponse] = {}
_task_streams: Dict[str, asyncio.Queue] = {}
_task_store_path = Path(settings.task_store_path)


def _ensure_store():
    _task_store_path.parent.mkdir(parents=True, exist_ok=True)


async def _save_task_to_store(task: TaskResponse):
    _ensure_store()
    try:
        async with aiofiles.open(_task_store_path, mode="a", encoding="utf-8") as f:
            await f.write(task.model_dump_json() + "\n")
    except Exception as exc:
        logger.error("Failed to append task to store: %s", exc)


def _load_tasks_from_store():
    if not _task_store_path.is_file():
        return
    try:
        with open(_task_store_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    task = TaskResponse(**data)
                    _tasks_cache[task.task_id] = task
                except Exception:
                    continue
    except Exception as exc:
        logger.warning("Could not read existing tasks store: %s", exc)


_load_tasks_from_store()


async def _execute_task_pipeline(task_id: str, request: TaskRequest):
    """Background task execution pipeline."""
    task = _tasks_cache.get(task_id)
    if not task:
        return

    task.status = TaskStatus.RUNNING
    start_time = time.monotonic()
    queue = _task_streams.get(task_id)

    def emit_event(event):
        if queue:
            try:
                queue.put_nowait(event.to_sse())
            except Exception:
                pass

    emit_event(StatusEvent(status="running", message="Task execution started", task_id=task_id))
    pipeline_type = task_router.route(request)

    try:
        # Audit log the prompt
        await audit_logger.log_model_call(
            prompt=request.prompt,
            model=request.model or settings.active_model_name,
            task_type=pipeline_type.value,
        )

        result_payload: Any = None
        artifacts: List[Dict[str, Any]] = []

        if pipeline_type == TaskType.AGENT:
            state = AgentState(
                task_id=task_id,
                prompt=request.prompt,
                max_steps=6,
            )
            completed_state = await agent_graph.run(state)
            result_payload = completed_state.final_output
            artifacts = completed_state.artifacts

        elif pipeline_type == TaskType.RAG:
            emit_event(StatusEvent(status="retrieving", message="Searching local knowledge base...", task_id=task_id))
            retrieved = await hybrid_retriever.retrieve(request.prompt, top_k=5)
            context_str = "\n\n".join(
                [f"[Source: {c.source}, Score: {c.score}]\n{c.text}" for c in retrieved]
            )

            prompt_with_context = f"Context from Sovereign Knowledge Base:\n{context_str}\n\nUser Question:\n{request.prompt}"
            client = model_registry.get_client(role="reasoning", model_id=request.model)

            gen_req = GenerationRequest(
                prompt=prompt_with_context,
                system_prompt=request.system_prompt or "Answer questions strictly based on the provided context.",
                temperature=request.temperature or 0.2,
            )
            response = await client.chat(gen_req)
            result_payload = response.content
            artifacts = [
                {"type": "rag_sources", "sources": [c.model_dump() for c in retrieved]}
            ]

        elif pipeline_type == TaskType.VISION:
            vision_client = VisionClient()
            if request.file_paths:
                file_path = request.file_paths[0]
                with open(file_path, "rb") as img_f:
                    img_bytes = img_f.read()
                resp = await vision_client.analyze_image(
                    image_bytes=img_bytes,
                    prompt=request.prompt,
                    temperature=request.temperature or 0.2,
                )
                result_payload = resp.content
            else:
                result_payload = "Vision task requested but no file_paths provided."

        elif pipeline_type == TaskType.SANDBOX:
            runner = DockerSandboxRunner()
            code_to_run = request.parameters.get("code") or request.prompt
            emit_event(StatusEvent(status="sandboxing", message="Spawning isolated Docker container...", task_id=task_id))
            sandbox_res = await runner.run_code(code_to_run, language="python")
            result_payload = {
                "stdout": sandbox_res.stdout,
                "stderr": sandbox_res.stderr,
                "exit_code": sandbox_res.exit_code,
                "timed_out": sandbox_res.timed_out,
            }
            artifacts = [{"type": "sandbox_execution", **result_payload}]

        else:
            # GENERAL / LLM reasoning
            client = model_registry.get_client(role="reasoning", model_id=request.model)
            gen_req = GenerationRequest(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature or 0.7,
            )
            response = await client.chat(gen_req)
            result_payload = response.content
            if response.reasoning_content:
                emit_event(ReasoningEvent(reasoning=response.reasoning_content, task_id=task_id))

        duration = time.monotonic() - start_time
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        task.execution_time_seconds = round(duration, 3)
        task.result = TaskResult(
            output=result_payload,
            artifacts=artifacts,
            model_used=request.model or settings.active_model_name,
            execution_time_seconds=round(duration, 3),
        )

        emit_event(TokenEvent(token=str(result_payload), task_id=task_id))
        emit_event(CompletionEvent(result=result_payload, execution_time_seconds=round(duration, 3), task_id=task_id))

    except Exception as exc:
        logger.error("Task %s failed: %s", task_id, exc, exc_info=True)
        duration = time.monotonic() - start_time
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now(timezone.utc)
        task.execution_time_seconds = round(duration, 3)
        task.error = str(exc)
        emit_event(ErrorEvent(error=str(exc), task_id=task_id))

    finally:
        await _save_task_to_store(task)
        if queue:
            # Send end marker to signal SSE stream finish
            await queue.put(None)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks) -> TaskResponse:
    """Dispatches a task for processing."""
    task = TaskResponse(
        task_type=request.task_type,
        status=TaskStatus.PENDING,
        prompt=request.prompt,
        metadata=request.metadata,
    )
    _tasks_cache[task.task_id] = task
    _task_streams[task.task_id] = asyncio.Queue()

    # Schedule non-blocking execution via BackgroundTasks
    background_tasks.add_task(_execute_task_pipeline, task.task_id, request)

    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
) -> TaskListResponse:
    """Lists all stored tasks with optional status filtering."""
    tasks = list(_tasks_cache.values())
    if status_filter:
        tasks = [t for t in tasks if t.status == status_filter]
    # Return newest first
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    return TaskListResponse(tasks=tasks[:limit], total=len(tasks))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Fetches full task status and result."""
    task = _tasks_cache.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return task


@router.delete("/{task_id}", response_model=TaskCancelResponse)
async def cancel_task(task_id: str) -> TaskCancelResponse:
    """Cancels a pending or running task."""
    task = _tasks_cache.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        return TaskCancelResponse(
            task_id=task_id,
            status=task.status,
            message="Task already finished; cannot cancel.",
        )

    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.now(timezone.utc)
    await _save_task_to_store(task)
    return TaskCancelResponse(task_id=task_id, status=TaskStatus.CANCELLED)


@router.get("/{task_id}/stream")
async def stream_task_events(task_id: str):
    """
    SSE streaming endpoint for real-time task progress and token generation.
    Connect via EventSource or fetch ReadableStream on client.
    """
    task = _tasks_cache.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    queue = _task_streams.get(task_id)
    if not queue:
        queue = asyncio.Queue()
        _task_streams[task_id] = queue

    async def event_generator() -> AsyncIterator[str]:
        # If task already completed before stream connected, emit completion directly
        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            yield CompletionEvent(result=task.result or task.error, task_id=task_id).to_sse()
            return

        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
