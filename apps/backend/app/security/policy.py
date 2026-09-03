"""
Role-based action policy engine.

Defines which task types, tools, and actions are permitted for each actor role.
Used by the API layer and agent graph to enforce authorization before execution.
"""

import logging
from typing import Any, Dict, FrozenSet, Optional, Set

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Role definitions and permission matrix
# --------------------------------------------------------------------------

class Role:
    """Known actor roles in the system."""
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


# Allowed task types per role
_TASK_TYPE_PERMISSIONS: Dict[str, FrozenSet[str]] = {
    Role.ADMIN: frozenset({"general", "rag", "agent", "vision", "document", "sandbox"}),
    Role.USER: frozenset({"general", "rag", "vision", "document"}),
    Role.AGENT: frozenset({"general", "rag", "vision", "document", "sandbox"}),
    Role.SYSTEM: frozenset({"general", "rag", "agent", "vision", "document", "sandbox"}),
}

# Allowed tools per role
_TOOL_PERMISSIONS: Dict[str, FrozenSet[str]] = {
    Role.ADMIN: frozenset({"calculator", "document_tool", "file_tool", "sandbox"}),
    Role.USER: frozenset({"calculator", "document_tool"}),
    Role.AGENT: frozenset({"calculator", "document_tool", "file_tool", "sandbox"}),
    Role.SYSTEM: frozenset({"calculator", "document_tool", "file_tool", "sandbox"}),
}

# Allowed actions per role
_ACTION_PERMISSIONS: Dict[str, FrozenSet[str]] = {
    Role.ADMIN: frozenset({
        "create_task", "cancel_task", "view_task", "list_tasks",
        "ingest_document", "query_knowledge", "view_audit",
        "manage_models",
    }),
    Role.USER: frozenset({
        "create_task", "view_task", "list_tasks",
        "ingest_document", "query_knowledge",
    }),
    Role.AGENT: frozenset({
        "create_task", "view_task", "query_knowledge",
    }),
    Role.SYSTEM: frozenset({
        "create_task", "cancel_task", "view_task", "list_tasks",
        "ingest_document", "query_knowledge", "view_audit",
        "manage_models",
    }),
}


class PolicyEngine:
    """
    Evaluates role-based permissions for task types, tools, and actions.
    Defaults to deny-all for unknown roles.
    """

    def check_task_type(self, role: str, task_type: str) -> bool:
        """Check if a role is allowed to create a task of the given type."""
        allowed = _TASK_TYPE_PERMISSIONS.get(role, frozenset())
        permitted = task_type in allowed
        if not permitted:
            logger.warning(
                "Policy denied: role=%s cannot create task_type=%s", role, task_type
            )
        return permitted

    def check_tool(self, role: str, tool_name: str) -> bool:
        """Check if a role is allowed to use a specific tool."""
        allowed = _TOOL_PERMISSIONS.get(role, frozenset())
        permitted = tool_name in allowed
        if not permitted:
            logger.warning(
                "Policy denied: role=%s cannot use tool=%s", role, tool_name
            )
        return permitted

    def check_action(self, role: str, action: str) -> bool:
        """Check if a role is allowed to perform a specific action."""
        allowed = _ACTION_PERMISSIONS.get(role, frozenset())
        permitted = action in allowed
        if not permitted:
            logger.warning(
                "Policy denied: role=%s cannot perform action=%s", role, action
            )
        return permitted

    def check_permission(self, role: str, action: str) -> bool:
        """
        General permission check — alias for check_action().
        This is the primary entry point used by API route handlers.
        """
        return self.check_action(role, action)

    def get_allowed_task_types(self, role: str) -> Set[str]:
        """Return the set of task types allowed for a role."""
        return set(_TASK_TYPE_PERMISSIONS.get(role, frozenset()))

    def get_allowed_tools(self, role: str) -> Set[str]:
        """Return the set of tools allowed for a role."""
        return set(_TOOL_PERMISSIONS.get(role, frozenset()))


# Singleton policy engine
policy_engine = PolicyEngine()
