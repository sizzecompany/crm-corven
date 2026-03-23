"""
CRM Corven — Tenants router (SUPERADMIN only).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Role
from app.database import get_db
from app.dependencies import require_role
from app.modules.tenants import service
from app.modules.tenants.schemas import TenantCreate, TenantOut, TenantUpdate

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/", response_model=list[TenantOut])
async def list_tenants(
    _user=require_role(Role.SUPERADMIN),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    tenants = await service.list_tenants(db, skip, limit)
    return [
        TenantOut(id=str(t.id), name=t.name, slug=t.slug, plan=t.plan,
                  is_active=t.is_active, settings=t.settings, created_at=t.created_at)
        for t in tenants
    ]


@router.post("/", response_model=TenantOut, status_code=201)
async def create_tenant(
    body: TenantCreate,
    _user=require_role(Role.SUPERADMIN),
    db: AsyncSession = Depends(get_db),
):
    tenant = await service.create_tenant(db, body)
    return TenantOut(id=str(tenant.id), name=tenant.name, slug=tenant.slug,
                     plan=tenant.plan, is_active=tenant.is_active,
                     settings=tenant.settings, created_at=tenant.created_at)


@router.patch("/{tenant_id}", response_model=TenantOut)
async def update_tenant(
    tenant_id: UUID,
    body: TenantUpdate,
    _user=require_role(Role.SUPERADMIN),
    db: AsyncSession = Depends(get_db),
):
    tenant = await service.update_tenant(db, tenant_id, body)
    return TenantOut(id=str(tenant.id), name=tenant.name, slug=tenant.slug,
                     plan=tenant.plan, is_active=tenant.is_active,
                     settings=tenant.settings, created_at=tenant.created_at)
