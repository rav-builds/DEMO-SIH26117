"""
Sandboxed file reader and writer tool.

Validates that all file operations are restricted to allowed directories only.
Prevents path traversal attacks and unauthorized filesystem access.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Allowed base directories for file operations (configurable)
_ALLOWED_DIRECTORIES: List[str] = [
    "data",
    "uploads",
    "tmp",
]


def _resolve_and_validate(file_path: str, allowed_dirs: Optional[List[str]] = None) -> Path:
    """
    Resolve the file path and validate it is within allowed directories.

    Raises:
        PermissionError: If the path is outside allowed directories.
        ValueError: If the path contains traversal patterns.
    """
    dirs = allowed_dirs or _ALLOWED_DIRECTORIES

    # Block obvious traversal patterns
    if ".." in file_path:
        raise PermissionError(f"Path traversal detected: {file_path}")

    resolved = Path(file_path).resolve()

    # Check if the resolved path is within any allowed directory
    for allowed in dirs:
        allowed_path = Path(allowed).resolve()
        try:
            resolved.relative_to(allowed_path)
            return resolved
        except ValueError:
            continue

    raise PermissionError(
        f"Access denied: {file_path} is not within allowed directories: {dirs}"
    )


async def read_file(
    file_path: str,
    max_size_bytes: int = 1_048_576,  # 1MB
    encoding: str = "utf-8",
) -> str:
    """
    Read a file from within allowed directories.

    Args:
        file_path: Path to the file (must be within allowed directories).
        max_size_bytes: Maximum file size to read (default 1MB).
        encoding: File encoding (default UTF-8).

    Returns:
        File contents as a string.

    Raises:
        PermissionError: If path is outside allowed directories.
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file exceeds max_size_bytes.
    """
    import asyncio

    resolved = _resolve_and_validate(file_path)

    if not resolved.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    size = resolved.stat().st_size
    if size > max_size_bytes:
        raise ValueError(
            f"File too large: {size} bytes exceeds limit of {max_size_bytes} bytes"
        )

    content = await asyncio.to_thread(resolved.read_text, encoding)
    logger.info("Read file: %s (%d bytes)", resolved, len(content))
    return content


async def write_file(
    file_path: str,
    content: str,
    encoding: str = "utf-8",
    max_size_bytes: int = 1_048_576,
) -> bool:
    """
    Write content to a file within allowed directories.

    Args:
        file_path: Target path (must be within allowed directories).
        content: String content to write.
        encoding: File encoding (default UTF-8).
        max_size_bytes: Maximum content size (default 1MB).

    Returns:
        True if the file was written successfully.

    Raises:
        PermissionError: If path is outside allowed directories.
        ValueError: If content exceeds max_size_bytes.
    """
    import asyncio

    if len(content.encode(encoding)) > max_size_bytes:
        raise ValueError(
            f"Content too large: exceeds limit of {max_size_bytes} bytes"
        )

    resolved = _resolve_and_validate(file_path)

    # Ensure parent directory exists
    resolved.parent.mkdir(parents=True, exist_ok=True)

    await asyncio.to_thread(resolved.write_text, content, encoding)
    logger.info("Wrote file: %s (%d bytes)", resolved, len(content))
    return True


# Tool schemas for agent tool calling
READ_FILE_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file. File must be within allowed directories (data/, uploads/, tmp/).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                },
            },
            "required": ["file_path"],
        },
    },
}

WRITE_FILE_TOOL_SCHEMA: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file. File must be within allowed directories (data/, uploads/, tmp/).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file.",
                },
            },
            "required": ["file_path", "content"],
        },
    },
}
