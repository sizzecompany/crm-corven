"""
CRM Corven — Campaigns module.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.models.campaign import Campaign
from app.models.lead import Lead


# ── Schemas ──────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    name: str
    source: str | None = None
    budget: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    description: str | None = None
    metadata_extra: dict | None = None


class CampaignUpdate(BaseModel):
    name: str | None = None
    source: str | None = None
    budget: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str | None = None
    description: str | None = None
    metadata_extra: dict | None = None


class CampaignOut(BaseModel):
    id: str
    name: str
    source: str | None = None
    budget: float | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    status: str
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignMetrics(BaseModel):
    campaign_id: str
    campaign_name: str
    total_leads: int = 0
    conversions: int = 0
    conversion_rate: float = 0.0
    cost_per_lead: float | None = None
    budget: float | None = None


# ── Service ──────────────────────────────────────────────────────────────────

async def list_campaigns(db: AsyncSession, tenant_id: UUID, skip: int = 0, limit: int = 50) -> list[Campaign]:
    result = await db.execute(
        select(Campaign)
        .where(Campaign.tenant_id == tenant_id)
        .order_by(Campaign.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_campaign(db: AsyncSession, tenant_id: UUID, campaign_id: UUID) -> Campaign:
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant_id)
    )
    campaign = result.scalar_one_or_none()
    if campaign is None:
        raise NotFoundError("Campaign", str(campaign_id))
    return campaign


async def create_campaign(db: AsyncSession, tenant_id: UUID, data: CampaignCreate) -> Campaign:
    campaign = Campaign(
        tenant_id=tenant_id,
        **data.model_dump(),
    )
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


async def update_campaign(db: AsyncSession, tenant_id: UUID, campaign_id: UUID, data: CampaignUpdate) -> Campaign:
    campaign = await get_campaign(db, tenant_id, campaign_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    await db.flush()
    await db.refresh(campaign)
    return campaign


async def get_campaign_metrics(db: AsyncSession, tenant_id: UUID, campaign_id: UUID) -> CampaignMetrics:
    campaign = await get_campaign(db, tenant_id, campaign_id)

    total_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.campaign_id == campaign_id, Lead.tenant_id == tenant_id)
    )
    total_leads = total_result.scalar() or 0

    conv_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.campaign_id == campaign_id,
            Lead.tenant_id == tenant_id,
            Lead.stage == "fechado",
        )
    )
    conversions = conv_result.scalar() or 0

    conversion_rate = (conversions / total_leads * 100) if total_leads > 0 else 0.0
    cost_per_lead = (campaign.budget / total_leads) if campaign.budget and total_leads > 0 else None

    return CampaignMetrics(
        campaign_id=str(campaign.id),
        campaign_name=campaign.name,
        total_leads=total_leads,
        conversions=conversions,
        conversion_rate=round(conversion_rate, 2),
        cost_per_lead=round(cost_per_lead, 2) if cost_per_lead else None,
        budget=campaign.budget,
    )


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


def _out(c: Campaign) -> CampaignOut:
    return CampaignOut(
        id=str(c.id), name=c.name, source=c.source, budget=c.budget,
        start_date=c.start_date, end_date=c.end_date, status=c.status,
        description=c.description, created_at=c.created_at,
    )


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns_endpoint(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    campaigns = await list_campaigns(db, current_user.tenant_id, skip, limit)
    return [_out(c) for c in campaigns]


@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign_endpoint(
    body: CampaignCreate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    campaign = await create_campaign(db, current_user.tenant_id, body)
    return _out(campaign)


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign_endpoint(
    campaign_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    campaign = await get_campaign(db, current_user.tenant_id, campaign_id)
    return _out(campaign)


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign_endpoint(
    campaign_id: UUID,
    body: CampaignUpdate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    campaign = await update_campaign(db, current_user.tenant_id, campaign_id, body)
    return _out(campaign)


@router.get("/{campaign_id}/metrics", response_model=CampaignMetrics)
async def get_campaign_metrics_endpoint(
    campaign_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await get_campaign_metrics(db, current_user.tenant_id, campaign_id)
