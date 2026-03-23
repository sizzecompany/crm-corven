"""
CRM Corven — Users module: schemas, service, router.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.models.user import User


# ── Schemas ──────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    phone: str | None = None
    role: str = "user"
    tenant_id: str | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    role: str | None = None
    is_active: bool | None = None
    custom_permissions: dict | None = None
    avatar_url: str | None = None


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    phone: str | None = None
    tenant_id: str | None = None
    is_active: bool
    avatar_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Service ──────────────────────────────────────────────────────────────────

async def list_users(
    db: AsyncSession, tenant_id: UUID | None = None, skip: int = 0, limit: int = 50
) -> list[User]:
    query = select(User)
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_user(db: AsyncSession, user_id: UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User", str(user_id))
    return user


async def create_user(
    db: AsyncSession,
    data: UserCreate,
    tenant_id: UUID | None = None,
) -> User:
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError(f"User with email '{data.email}' already exists")

    user = User(
        email=data.email,
        name=data.name,
        phone=data.phone,
        role=data.role,
        tenant_id=tenant_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate) -> User:
    user = await get_user(db, user_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/users", tags=["Users"])


def _to_out(u: User) -> UserOut:
    return UserOut(
        id=str(u.id), email=u.email, name=u.name, role=u.role,
        phone=u.phone, tenant_id=str(u.tenant_id) if u.tenant_id else None,
        is_active=u.is_active, avatar_url=u.avatar_url, created_at=u.created_at,
    )


@router.get("/", response_model=list[UserOut])
async def list_users_endpoint(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List users. ADMIN sees own tenant users; SUPERADMIN sees all."""
    tenant_filter = None
    if Role(current_user.role) != Role.SUPERADMIN:
        tenant_filter = current_user.tenant_id
    users = await list_users(db, tenant_filter, skip, limit)
    return [_to_out(u) for u in users]


@router.post("/", response_model=UserOut, status_code=201)
async def create_user_endpoint(
    body: UserCreate,
    current_user: CurrentUser = require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    actor_role = Role(current_user.role)
    effective_tenant_id = (
        UUID(body.tenant_id) if actor_role == Role.SUPERADMIN and body.tenant_id else current_user.tenant_id
    )
    user = await create_user(db, body, effective_tenant_id)
    return _to_out(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(
    user_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, user_id)
    # Tenant isolation: non-superadmins can only see their own tenant's users
    if Role(current_user.role) != Role.SUPERADMIN and user.tenant_id != current_user.tenant_id:
        raise NotFoundError("User", str(user_id))
    return _to_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: UUID,
    body: UserUpdate,
    current_user: CurrentUser = require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    target_user = await get_user(db, user_id)
    if Role(current_user.role) != Role.SUPERADMIN and target_user.tenant_id != current_user.tenant_id:
        raise NotFoundError("User", str(user_id))

    user = await update_user(db, user_id, body)
    return _to_out(user)
