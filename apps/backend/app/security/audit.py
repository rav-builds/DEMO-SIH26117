"""
Append-only JSONL audit logger for sovereign compliance.

Records all model prompts, tool executions, and security events to an immutable
JSONL file. Each line is a self-contained JSON object with a SHA-256 prompt hash.
Uses aiofiles for non-blocking writes.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

import aiofiles

from app.config import settings

logger = logging.getLogger(__name__)


class AuditEvent:
    """Single audit log entry."""

    __slots__ = (
        "event_id", "timestamp", "event_type", "actor",
        "prompt_hash", "details", "ip_address",
    )

    def __init__(
        self,
        event_type: str,
        actor: str = "system",
        details: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        ip_address: Optional[str] = None,
    ):
        self.event_id = str(uuid4())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.event_type = event_type
        self.actor = actor
        self.prompt_hash = (
            hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            if prompt
            else None
        )
        self.details = details or {}
        self.ip_address = ip_address

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "prompt_hash": self.prompt_hash,
            "details": self.details,
            "ip_address": self.ip_address,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


class AuditLogger:
    """
    Append-only JSONL audit logger.

    All writes are append-only — no updates or deletes are ever performed.
    This ensures a tamper-evident audit trail for sovereign compliance.
    """

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path or settings.audit_log_path)
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Create the audit log directory if it doesn't exist."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def log_event(
        self,
        event_type: str,
        actor: str = "system",
        details: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """
        Append an audit event to the JSONL log file.

        Returns the event_id of the recorded event.
        """
        event = AuditEvent(
            event_type=event_type,
            actor=actor,
            details=details,
            prompt=prompt,
            ip_address=ip_address,
        )

        try:
            async with aiofiles.open(self.log_path, mode="a", encoding="utf-8") as f:
                await f.write(event.to_json_line() + "\n")
        except Exception as exc:
            logger.error("Failed to write audit event: %s", exc)
            raise

        return event.event_id

    async def log_model_call(
        self,
        prompt: str,
        model: str,
        task_type: str,
        actor: str = "user",
        ip_address: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Convenience method to log a model inference call."""
        details = {
            "model": model,
            "task_type": task_type,
            "prompt_length": len(prompt),
            **(extra or {}),
        }
        return await self.log_event(
            event_type="model_call",
            actor=actor,
            details=details,
            prompt=prompt,
            ip_address=ip_address,
        )

    async def log_tool_execution(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        actor: str = "agent",
        ip_address: Optional[str] = None,
    ) -> str:
        """Convenience method to log a tool execution by the agent."""
        return await self.log_event(
            event_type="tool_execution",
            actor=actor,
            details={"tool_name": tool_name, "tool_input": tool_input},
            ip_address=ip_address,
        )

    async def log_security_event(
        self,
        event_subtype: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """Log a security-related event (access denied, policy violation, etc.)."""
        return await self.log_event(
            event_type=f"security.{event_subtype}",
            actor="security",
            details=details,
            ip_address=ip_address,
        )

    async def query_log(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Read and filter audit log entries.

        Args:
            event_type: Filter by event type (prefix match).
            start_time: ISO timestamp lower bound.
            end_time: ISO timestamp upper bound.
            limit: Maximum number of entries to return.
        """
        results: List[Dict[str, Any]] = []

        if not self.log_path.is_file():
            return results

        try:
            async with aiofiles.open(self.log_path, mode="r", encoding="utf-8") as f:
                async for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Apply filters
                    if event_type and not entry.get("event_type", "").startswith(event_type):
                        continue
                    if start_time and entry.get("timestamp", "") < start_time:
                        continue
                    if end_time and entry.get("timestamp", "") > end_time:
                        continue

                    results.append(entry)
                    if len(results) >= limit:
                        break
        except Exception as exc:
            logger.error("Failed to read audit log: %s", exc)

        return results


# Singleton audit logger instance
audit_logger = AuditLogger()
