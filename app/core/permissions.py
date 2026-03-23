"""
CRM Corven — Granular permissions system.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from fastapi import HTTPException, status


class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"


class Resource(str, Enum):
    LEADS = "leads"
    USERS = "users"
    TENANTS = "tenants"
    CAMPAIGNS = "campaigns"
    WHATSAPP = "whatsapp"
    DOCUMENTS = "documents"
    CALENDAR = "calendar"
    AUTOMATIONS = "automations"
    SETTINGS = "settings"
    DASHBOARD = "dashboard"
    AGENT = "agent"


class Action(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"  # full control


# Default permissions by role
DEFAULT_PERMISSIONS: dict[Role, dict[Resource, list[Action]]] = {
    Role.SUPERADMIN: {
        resource: [Action.MANAGE] for resource in Resource
    },
    Role.ADMIN: {
        Resource.LEADS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.USERS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.CAMPAIGNS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.WHATSAPP: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.DOCUMENTS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.CALENDAR: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.AUTOMATIONS: [Action.CREATE, Action.READ, Action.UPDATE, Action.DELETE],
        Resource.SETTINGS: [Action.READ, Action.UPDATE],
        Resource.DASHBOARD: [Action.READ],
        Resource.AGENT: [Action.CREATE, Action.READ],
    },
    Role.USER: {
        Resource.LEADS: [Action.CREATE, Action.READ, Action.UPDATE],
        Resource.CAMPAIGNS: [Action.READ],
        Resource.WHATSAPP: [Action.READ],
        Resource.DOCUMENTS: [Action.READ],
        Resource.CALENDAR: [Action.CREATE, Action.READ, Action.UPDATE],
        Resource.SETTINGS: [Action.READ],
        Resource.DASHBOARD: [Action.READ],
        Resource.AGENT: [Action.READ],
    },
}


def check_permission(
    role: Role,
    resource: Resource,
    action: Action,
    custom_permissions: Optional[dict] = None,
) -> bool:
    """
    Check if a role has a given action on a resource.
    Custom permission overrides (from DB) take precedence.
    """
    # Check custom permissions first
    if custom_permissions:
        resource_perms = custom_permissions.get(resource.value, [])
        if Action.MANAGE.value in resource_perms or action.value in resource_perms:
            return True

    # Fallback to default role permissions
    role_perms = DEFAULT_PERMISSIONS.get(role, {})
    resource_actions = role_perms.get(resource, [])

    return Action.MANAGE in resource_actions or action in resource_actions


def require_permission(
    role: Role,
    resource: Resource,
    action: Action,
    custom_permissions: Optional[dict] = None,
) -> None:
    """Raise 403 if permission is denied."""
    if not check_permission(role, resource, action, custom_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {action.value} on {resource.value}",
        )
