"""
CRM Corven — Automations module.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.models.automation import AutomationRule


# ── Schemas ──────────────────────────────────────────────────────────────────

class AutomationCreate(BaseModel):
    name: str
    description: str | None = None
    trigger: str  # lead_idle, new_message, lead_created, lead_stage_changed
    conditions: dict = {}
    actions: dict = {}
    is_active: bool = True


class AutomationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    trigger: str | None = None
    conditions: dict | None = None
    actions: dict | None = None
    is_active: bool | None = None


class AutomationOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    trigger: str
    conditions: dict
    actions: dict
    is_active: bool
    last_run_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Service ──────────────────────────────────────────────────────────────────

async def list_automations(db: AsyncSession, tenant_id: UUID) -> list[AutomationRule]:
    result = await db.execute(
        select(AutomationRule)
        .where(AutomationRule.tenant_id == tenant_id)
        .order_by(AutomationRule.created_at.desc())
    )
    return list(result.scalars().all())


async def get_automation(db: AsyncSession, tenant_id: UUID, rule_id: UUID) -> AutomationRule:
    result = await db.execute(
        select(AutomationRule).where(
            AutomationRule.id == rule_id, AutomationRule.tenant_id == tenant_id
        )
    )
    rule = result.scalar_one_or_none()
    if rule is None:
        raise NotFoundError("Automation Rule", str(rule_id))
    return rule


async def create_automation(db: AsyncSession, tenant_id: UUID, data: AutomationCreate) -> AutomationRule:
    rule = AutomationRule(
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


async def update_automation(
    db: AsyncSession, tenant_id: UUID, rule_id: UUID, data: AutomationUpdate
) -> AutomationRule:
    rule = await get_automation(db, tenant_id, rule_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    await db.flush()
    await db.refresh(rule)
    return rule


async def delete_automation(db: AsyncSession, tenant_id: UUID, rule_id: UUID) -> None:
    rule = await get_automation(db, tenant_id, rule_id)
    await db.delete(rule)
    await db.flush()


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/automations", tags=["Automations"])


def _out(r: AutomationRule) -> AutomationOut:
    return AutomationOut(
        id=str(r.id), name=r.name, description=r.description,
        trigger=r.trigger, conditions=r.conditions, actions=r.actions,
        is_active=r.is_active, last_run_at=r.last_run_at, created_at=r.created_at,
    )


@router.get("/", response_model=list[AutomationOut])
async def list_automations_endpoint(
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    rules = await list_automations(db, current_user.tenant_id)
    return [_out(r) for r in rules]


@router.post("/", response_model=AutomationOut, status_code=201)
async def create_automation_endpoint(
    body: AutomationCreate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    rule = await create_automation(db, current_user.tenant_id, body)
    return _out(rule)


@router.get("/{rule_id}", response_model=AutomationOut)
async def get_automation_endpoint(
    rule_id: UUID,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    rule = await get_automation(db, current_user.tenant_id, rule_id)
    return _out(rule)


@router.patch("/{rule_id}", response_model=AutomationOut)
async def update_automation_endpoint(
    rule_id: UUID,
    body: AutomationUpdate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    rule = await update_automation(db, current_user.tenant_id, rule_id, body)
    return _out(rule)


@router.delete("/{rule_id}", status_code=204)
async def delete_automation_endpoint(
    rule_id: UUID,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    await delete_automation(db, current_user.tenant_id, rule_id)
