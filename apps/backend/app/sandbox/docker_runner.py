"""
Docker-based sandboxed code execution runner.

Executes user-generated code in a fully isolated Docker container with strict
resource limits. Uses asyncio.create_subprocess_exec for non-blocking execution.
"""

import asyncio
import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from app.sandbox.limits import SandboxLimits

logger = logging.getLogger(__name__)


class SandboxResult(BaseModel):
    """Result of a sandboxed code execution."""

    exit_code: int = Field(..., description="Process exit code")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    duration_seconds: float = Field(..., description="Execution wall-clock time in seconds")
    timed_out: bool = Field(default=False, description="Whether execution was killed due to timeout")
    truncated: bool = Field(default=False, description="Whether output was truncated")

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out


_MAX_OUTPUT_BYTES = 64 * 1024  # 64KB max output capture


class DockerSandboxRunner:
    """
    Executes code inside a Docker container with strict isolation.

    Usage:
        runner = DockerSandboxRunner()
        result = await runner.run_code("print('hello')", language="python")
    """

    def __init__(self, limits: Optional[SandboxLimits] = None):
        self.limits = limits or SandboxLimits()

    async def run_code(
        self,
        code: str,
        language: str = "python",
        timeout_override: Optional[int] = None,
    ) -> SandboxResult:
        """
        Execute code in a sandboxed Docker container.

        Args:
            code: Source code string to execute.
            language: Programming language (currently only 'python' supported).
            timeout_override: Override the default timeout in seconds.

        Returns:
            SandboxResult with stdout, stderr, exit code, and timing.
        """
        if language != "python":
            return SandboxResult(
                exit_code=1,
                stderr=f"Unsupported language: {language}. Only 'python' is supported.",
                duration_seconds=0.0,
            )

        timeout = timeout_override or self.limits.timeout_seconds

        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            prefix="sandbox_",
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            result = await self._execute_in_docker(tmp_path, timeout)
        finally:
            # Clean up temp file
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass

        return result

    async def _execute_in_docker(
        self,
        code_file: str,
        timeout: int,
    ) -> SandboxResult:
        """Run the code file inside a Docker container."""
        docker_args = self.limits.to_docker_args()
        container_code_path = "/tmp/code.py"

        cmd = [
            "docker", "run",
            *docker_args,
            "-v", f"{code_file}:{container_code_path}:ro",
            self.limits.docker_image,
            "python", container_code_path,
        ]

        logger.info("Executing sandbox: %s", " ".join(cmd))
        start_time = time.monotonic()

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
                timed_out = False
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stdout_bytes = b""
                stderr_bytes = b"Execution timed out and was terminated."
                timed_out = True

            duration = time.monotonic() - start_time

            # Truncate large outputs
            stdout_str = stdout_bytes[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            stderr_str = stderr_bytes[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace")
            truncated = (
                len(stdout_bytes) > _MAX_OUTPUT_BYTES
                or len(stderr_bytes) > _MAX_OUTPUT_BYTES
            )

            return SandboxResult(
                exit_code=process.returncode or 1,
                stdout=stdout_str,
                stderr=stderr_str,
                duration_seconds=round(duration, 3),
                timed_out=timed_out,
                truncated=truncated,
            )

        except FileNotFoundError:
            return SandboxResult(
                exit_code=127,
                stderr="Docker is not installed or not in PATH.",
                duration_seconds=0.0,
            )
        except Exception as exc:
            logger.error("Sandbox execution error: %s", exc)
            return SandboxResult(
                exit_code=1,
                stderr=f"Sandbox execution error: {exc}",
                duration_seconds=time.monotonic() - start_time,
            )

    async def check_docker_available(self) -> bool:
        """Check if Docker daemon is running and accessible."""
        try:
            process = await asyncio.create_subprocess_exec(
                "docker", "info",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(process.wait(), timeout=5.0)
            return process.returncode == 0
        except Exception:
            return False
