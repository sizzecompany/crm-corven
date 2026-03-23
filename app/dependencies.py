"""
CRM Corven — Common FastAPI dependencies.
"""

from __future__ import annotations

from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Action, Resource, Role, require_permission
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Depends(security_scheme)
    ] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode JWT, load user from DB, and set tenant_id on request.state.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Set tenant context on the request
    request.state.tenant_id = user.tenant_id
    request.state.user = user

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


def require_role(*roles: Role):
    """Dependency factory that restricts access to certain roles."""

    async def _check(user: CurrentUser):
        if Role(user.role) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user

    return Depends(_check)


def require_resource_permission(resource: Resource, action: Action):
    """Dependency factory for granular resource+action check."""

    async def _check(user: CurrentUser):
        require_permission(
            role=Role(user.role),
            resource=resource,
            action=action,
            custom_permissions=user.custom_permissions,
        )
        return user

    return Depends(_check)
