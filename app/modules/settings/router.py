"""
CRM Corven — Settings module.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.models.tenant import Tenant
from app.models.user import User


# ── Schemas ──────────────────────────────────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


class ProfileOut(BaseModel):
    id: str
    email: str
    name: str
    phone: str | None = None
    avatar_url: str | None = None
    role: str

    class Config:
        from_attributes = True


class CompanyUpdate(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    settings: dict | None = None


class CompanyOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    logo_url: str | None = None
    settings: dict | None = None

    class Config:
        from_attributes = True


class IntegrationStatus(BaseModel):
    whatsapp_evolution: bool = False
    whatsapp_meta: bool = False
    openai: bool = False
    s3_storage: bool = False


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/profile", response_model=ProfileOut)
async def get_profile(current_user: CurrentUser):
    return ProfileOut(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
    )


@router.patch("/profile", response_model=ProfileOut)
async def update_profile(
    body: ProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    await db.refresh(current_user)
    return ProfileOut(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
    )


@router.get("/company", response_model=CompanyOut)
async def get_company(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Company")
    return CompanyOut(
        id=str(tenant.id), name=tenant.name, slug=tenant.slug,
        plan=tenant.plan, logo_url=tenant.logo_url, settings=tenant.settings,
    )


@router.patch("/company", response_model=CompanyOut)
async def update_company(
    body: CompanyUpdate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    result = await db.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    if tenant is None:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Company")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    await db.flush()
    await db.refresh(tenant)

    return CompanyOut(
        id=str(tenant.id), name=tenant.name, slug=tenant.slug,
        plan=tenant.plan, logo_url=tenant.logo_url, settings=tenant.settings,
    )


@router.get("/integrations", response_model=IntegrationStatus)
async def get_integrations(current_user: CurrentUser):
    """Check status of configured integrations."""
    from app.config import get_settings
    s = get_settings()
    return IntegrationStatus(
        whatsapp_evolution=bool(s.EVOLUTION_API_KEY),
        whatsapp_meta=bool(s.META_WHATSAPP_TOKEN),
        openai=bool(s.OPENAI_API_KEY),
        s3_storage=bool(s.S3_ACCESS_KEY),
    )
