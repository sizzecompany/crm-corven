"""
CRM Corven — Tenants service.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.tenant import Tenant
from app.modules.tenants.schemas import TenantCreate, TenantUpdate


async def list_tenants(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Tenant]:
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_tenant(db: AsyncSession, tenant_id: UUID) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise NotFoundError("Tenant", str(tenant_id))
    return tenant


async def create_tenant(db: AsyncSession, data: TenantCreate) -> Tenant:
    # Check slug uniqueness
    result = await db.execute(select(Tenant).where(Tenant.slug == data.slug))
    if result.scalar_one_or_none():
        raise ConflictError(f"Tenant with slug '{data.slug}' already exists")

    tenant = Tenant(**data.model_dump())
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)
    return tenant


async def update_tenant(db: AsyncSession, tenant_id: UUID, data: TenantUpdate) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    await db.flush()
    await db.refresh(tenant)
    return tenant
