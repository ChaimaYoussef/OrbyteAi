"""Custom Granular RBAC (Role-Based Access Control) Module.

Extends standard Orbyte roles (ADMIN, CURATOR, BASIC) with customizable fine-grained permissions:
- AGENT_CREATOR: Can build custom agents without needing full group curator rights.
- SECURITY_AUDITOR: Access to query history, audit logs, and compliance without query/chat rights.
- DOCUMENT_MANAGER: Can index documents into group document sets.
"""

from enum import Enum
from typing import Set
from pydantic import BaseModel


class ExtendedPermission(str, Enum):
    CREATE_AGENTS = "create_agents"
    MANAGE_DOCUMENTS = "manage_documents"
    VIEW_QUERY_HISTORY = "view_query_history"
    MANAGE_JOIN_LINKS = "manage_join_links"
    VIEW_SECURITY_AUDIT = "view_security_audit"
    MANAGE_CONNECTORS = "manage_connectors"


class CustomRole(BaseModel):
    name: str
    description: str
    permissions: Set[ExtendedPermission]


# Pre-defined enterprise roles
DEFAULT_CUSTOM_ROLES: dict[str, CustomRole] = {
    "AGENT_CREATOR": CustomRole(
        name="Agent Creator",
        description="Can build and publish custom AI agents without group curator rights.",
        permissions={
            ExtendedPermission.CREATE_AGENTS,
        },
    ),
    "SECURITY_AUDITOR": CustomRole(
        name="Security Auditor",
        description="Access to security logs, query history, and DLP compliance reports.",
        permissions={
            ExtendedPermission.VIEW_QUERY_HISTORY,
            ExtendedPermission.VIEW_SECURITY_AUDIT,
        },
    ),
    "DOCUMENT_MANAGER": CustomRole(
        name="Document Manager",
        description="Can attach and manage documents and connectors for assigned groups.",
        permissions={
            ExtendedPermission.MANAGE_DOCUMENTS,
            ExtendedPermission.MANAGE_CONNECTORS,
        },
    ),
}


def user_has_custom_permission(
    user_permissions: Set[str], required_permission: ExtendedPermission
) -> bool:
    """Check if a user possesses a specific fine-grained permission."""
    return required_permission.value in user_permissions
