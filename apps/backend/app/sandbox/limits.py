"""
Sandbox resource limits and Docker flag generation.

Enforces strict isolation: memory cap, network disabled, auto-remove,
CPU throttle, read-only filesystem, and PID limit.
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.config import settings


class SandboxLimits(BaseModel):
    """Immutable sandbox resource constraints for Docker container execution."""

    memory_mb: int = Field(
        default_factory=lambda: settings.sandbox_max_memory_mb,
        description="Maximum container memory in MB",
    )
    cpu_limit: float = Field(
        default=1.0,
        ge=0.1,
        le=4.0,
        description="CPU core limit (fractional allowed)",
    )
    timeout_seconds: int = Field(
        default_factory=lambda: settings.sandbox_timeout_seconds,
        description="Maximum execution time in seconds",
    )
    network_disabled: bool = Field(
        default=True,
        description="Disable all network access inside the container",
    )
    read_only_fs: bool = Field(
        default=True,
        description="Mount filesystem as read-only (except /tmp)",
    )
    pids_limit: int = Field(
        default=64,
        ge=1,
        le=256,
        description="Maximum number of processes inside the container",
    )
    auto_remove: bool = Field(
        default=True,
        description="Automatically remove the container after exit",
    )
    docker_image: str = Field(
        default="python:3.11-slim",
        description="Base Docker image for code execution",
    )

    def to_docker_args(self) -> List[str]:
        """
        Generate Docker CLI flags for strict sandbox isolation.

        Returns a list of strings suitable for passing to `docker run`.
        """
        args: List[str] = []

        # Memory limit
        args.append(f"--memory={self.memory_mb}m")
        args.append(f"--memory-swap={self.memory_mb}m")  # No swap

        # CPU limit
        args.append(f"--cpus={self.cpu_limit}")

        # Network isolation
        if self.network_disabled:
            args.append("--network=none")

        # Read-only filesystem with writable /tmp
        if self.read_only_fs:
            args.append("--read-only")
            args.append("--tmpfs=/tmp:rw,noexec,nosuid,size=64m")

        # PID limit
        args.append(f"--pids-limit={self.pids_limit}")

        # Auto-remove
        if self.auto_remove:
            args.append("--rm")

        # Security: drop all capabilities, no new privileges
        args.append("--cap-drop=ALL")
        args.append("--security-opt=no-new-privileges")

        return args

    def to_summary(self) -> dict:
        """Return a human-readable summary of the sandbox limits."""
        return {
            "memory": f"{self.memory_mb}MB",
            "cpu": f"{self.cpu_limit} cores",
            "timeout": f"{self.timeout_seconds}s",
            "network": "disabled" if self.network_disabled else "enabled",
            "filesystem": "read-only" if self.read_only_fs else "read-write",
            "pids_limit": self.pids_limit,
            "auto_remove": self.auto_remove,
            "image": self.docker_image,
        }
