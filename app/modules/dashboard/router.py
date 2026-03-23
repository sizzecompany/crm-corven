"""
CRM Corven — Dashboard module.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser
from app.models.lead import Lead, LeadStage
from app.models.campaign import Campaign
from app.models.task import Task


# ── Schemas ──────────────────────────────────────────────────────────────────

class DashboardMetrics(BaseModel):
    total_leads: int = 0
    leads_by_stage: dict[str, int] = {}
    leads_by_source: dict[str, int] = {}
    conversions: int = 0
    conversion_rate: float = 0.0
    total_campaigns: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0


class UserDashboardMetrics(BaseModel):
    my_leads: int = 0
    my_leads_by_stage: dict[str, int] = {}
    my_pending_tasks: int = 0
    my_conversions: int = 0


# ── Service ──────────────────────────────────────────────────────────────────

async def get_admin_dashboard(db: AsyncSession, tenant_id: UUID) -> DashboardMetrics:
    # Total leads
    total_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id)
    )
    total_leads = total_result.scalar() or 0

    # Leads by stage
    stage_result = await db.execute(
        select(Lead.stage, func.count(Lead.id))
        .where(Lead.tenant_id == tenant_id)
        .group_by(Lead.stage)
    )
    leads_by_stage = {row[0]: row[1] for row in stage_result.all()}

    # Leads by source
    source_result = await db.execute(
        select(Lead.source, func.count(Lead.id))
        .where(Lead.tenant_id == tenant_id, Lead.source.isnot(None))
        .group_by(Lead.source)
    )
    leads_by_source = {row[0]: row[1] for row in source_result.all()}

    # Conversions (closed leads)
    conversions = leads_by_stage.get(LeadStage.FECHADO.value, 0)
    conversion_rate = (conversions / total_leads * 100) if total_leads > 0 else 0.0

    # Campaigns
    campaigns_result = await db.execute(
        select(func.count(Campaign.id)).where(Campaign.tenant_id == tenant_id)
    )
    total_campaigns = campaigns_result.scalar() or 0

    # Tasks
    pending_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id, Task.status == "pending"
        )
    )
    pending_tasks = pending_result.scalar() or 0

    from datetime import datetime, timezone
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.status == "pending",
            Task.due_date < datetime.now(timezone.utc),
        )
    )
    overdue_tasks = overdue_result.scalar() or 0

    return DashboardMetrics(
        total_leads=total_leads,
        leads_by_stage=leads_by_stage,
        leads_by_source=leads_by_source,
        conversions=conversions,
        conversion_rate=round(conversion_rate, 2),
        total_campaigns=total_campaigns,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
    )


async def get_user_dashboard(db: AsyncSession, tenant_id: UUID, user_id: UUID) -> UserDashboardMetrics:
    # My leads
    total_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id, Lead.assigned_to == user_id
        )
    )
    my_leads = total_result.scalar() or 0

    # My leads by stage
    stage_result = await db.execute(
        select(Lead.stage, func.count(Lead.id))
        .where(Lead.tenant_id == tenant_id, Lead.assigned_to == user_id)
        .group_by(Lead.stage)
    )
    my_leads_by_stage = {row[0]: row[1] for row in stage_result.all()}

    # My pending tasks
    tasks_result = await db.execute(
        select(func.count(Task.id)).where(
            Task.tenant_id == tenant_id,
            Task.assigned_to == user_id,
            Task.status == "pending",
        )
    )
    my_pending_tasks = tasks_result.scalar() or 0

    my_conversions = my_leads_by_stage.get(LeadStage.FECHADO.value, 0)

    return UserDashboardMetrics(
        my_leads=my_leads,
        my_leads_by_stage=my_leads_by_stage,
        my_pending_tasks=my_pending_tasks,
        my_conversions=my_conversions,
    )


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/admin", response_model=DashboardMetrics)
async def admin_dashboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Admin dashboard: global metrics for the entire tenant."""
    if Role(current_user.role) == Role.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient role",
        )
    return await get_admin_dashboard(db, current_user.tenant_id)


@router.get("/user", response_model=UserDashboardMetrics)
async def user_dashboard(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """User dashboard: individual performance metrics."""
    return await get_user_dashboard(db, current_user.tenant_id, current_user.id)
