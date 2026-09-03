"""
Security & Audit API routes.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query

from app.schemas.response import APIResponse
from app.security.audit import audit_logger
from app.security.network import egress_guard
from app.security.policy import policy_engine

router = APIRouter(prefix="/security")


@router.get("/audit", response_model=APIResponse[List[Dict[str, Any]]])
async def get_audit_trail(
    event_type: Optional[str] = Query(None, description="Prefix filter for event type"),
    start_time: Optional[str] = Query(None, description="ISO timestamp start"),
    end_time: Optional[str] = Query(None, description="ISO timestamp end"),
    limit: int = Query(50, ge=1, le=500),
) -> APIResponse[List[Dict[str, Any]]]:
    """Queries the append-only cryptographic audit trail."""
    try:
        entries = await audit_logger.query_log(
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        return APIResponse.ok(data=entries)
    except Exception as exc:
        return APIResponse.fail(error=f"Failed to query audit logs: {str(exc)}")


@router.get("/status", response_model=APIResponse[Dict[str, Any]])
async def get_security_status() -> APIResponse[Dict[str, Any]]:
    """Returns air-gap verification and egress firewall policy telemetry."""
    status_info = egress_guard.get_status()
    return APIResponse.ok(data=status_info)


@router.get("/policies", response_model=APIResponse[Dict[str, Any]])
async def get_role_policies(role: str = Query("user")) -> APIResponse[Dict[str, Any]]:
    """Returns permission policies for a given role."""
    data = {
        "role": role,
        "allowed_task_types": list(policy_engine.get_allowed_task_types(role)),
        "allowed_tools": list(policy_engine.get_allowed_tools(role)),
    }
    return APIResponse.ok(data=data)
