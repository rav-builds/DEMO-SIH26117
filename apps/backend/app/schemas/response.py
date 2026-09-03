"""
Standardized API response envelope schemas.
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standardized top-level response envelope for API endpoints."""
    success: bool = Field(default=True, description="Indicates if operation succeeded")
    data: Optional[T] = Field(default=None, description="Payload data returned by endpoint")
    error: Optional[str] = Field(default=None, description="Error message if operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Contextual or debug metadata")

    @classmethod
    def ok(cls, data: T, metadata: Optional[Dict[str, Any]] = None) -> "APIResponse[T]":
        return cls(success=True, data=data, metadata=metadata or {})

    @classmethod
    def fail(cls, error: str, metadata: Optional[Dict[str, Any]] = None) -> "APIResponse[None]":
        return cls(success=False, data=None, error=error, metadata=metadata or {})
