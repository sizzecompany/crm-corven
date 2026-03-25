from __future__ import annotations

from datetime import datetime, timezone, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.lead_qualification import LeadQualification
from app.models.campaign import Campaign
from app.models.whatsapp import Message


async def first_response_time_seconds(db: AsyncSession, tenant_id: UUID, window_days: int = 30) -> float:
    start = datetime.now(timezone.utc) - timedelta(days=window_days)

    result = await db.execute(
        select(Lead.id, Lead.created_at)
        .where(Lead.tenant_id == tenant_id, Lead.created_at >= start)
    )
    leads = result.all()
    if not leads:
        return 0.0

    total = 0.0
    counted = 0
    for lead_id, created_at in leads:
        msg_result = await db.execute(
            select(Message.created_at)
            .where(
                Message.tenant_id == tenant_id,
                Message.lead_id == lead_id,
                Message.direction == "outbound",
            )
            .order_by(Message.created_at.asc())
            .limit(1)
        )
        first_msg = msg_result.scalar_one_or_none()
        if not first_msg:
            continue
        total += (first_msg - created_at).total_seconds()
        counted += 1

    return round(total / counted, 2) if counted else 0.0


async def qualification_rate(db: AsyncSession, tenant_id: UUID, window_days: int = 30) -> float:
    start = datetime.now(timezone.utc) - timedelta(days=window_days)

    total_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id, Lead.created_at >= start)
    )
    total = total_result.scalar() or 0
    if total == 0:
        return 0.0

    qualified_result = await db.execute(
        select(func.count(LeadQualification.id)).where(
            LeadQualification.tenant_id == tenant_id,
            LeadQualification.status == "qualified",
            LeadQualification.created_at >= start,
        )
    )
    qualified = qualified_result.scalar() or 0
    return round((qualified / total) * 100, 2)


async def conversion_rate(db: AsyncSession, tenant_id: UUID, window_days: int = 30) -> float:
    start = datetime.now(timezone.utc) - timedelta(days=window_days)

    total_result = await db.execute(
        select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id, Lead.created_at >= start)
    )
    total = total_result.scalar() or 0
    if total == 0:
        return 0.0

    converted_result = await db.execute(
        select(func.count(Lead.id)).where(
            Lead.tenant_id == tenant_id,
            Lead.stage == "fechado",
            Lead.created_at >= start,
        )
    )
    converted = converted_result.scalar() or 0
    return round((converted / total) * 100, 2)


async def cost_per_conversion_by_source(db: AsyncSession, tenant_id: UUID, window_days: int = 30) -> dict[str, float]:
    start = datetime.now(timezone.utc) - timedelta(days=window_days)
    source_cost: dict[str, float] = {}

    campaigns_result = await db.execute(
        select(Campaign.source, func.sum(Campaign.budget))
        .where(Campaign.tenant_id == tenant_id, Campaign.source.isnot(None), Campaign.budget.isnot(None))
        .group_by(Campaign.source)
    )
    for source, spend in campaigns_result.all():
        source_cost[source] = float(spend or 0)

    conv_result = await db.execute(
        select(Lead.source, func.count(Lead.id))
        .where(
            Lead.tenant_id == tenant_id,
            Lead.stage == "fechado",
            Lead.source.isnot(None),
            Lead.created_at >= start,
        )
        .group_by(Lead.source)
    )
    output: dict[str, float] = {}
    for source, conversions in conv_result.all():
        spend = source_cost.get(source, 0.0)
        output[source] = round(spend / conversions, 2) if conversions else 0.0
    return output


async def time_to_qualification_hours(db: AsyncSession, tenant_id: UUID, window_days: int = 30) -> dict[str, float]:
    start = datetime.now(timezone.utc) - timedelta(days=window_days)
    result = await db.execute(
        select(Lead.created_at, Lead.qualified_at, Lead.source)
        .where(
            Lead.tenant_id == tenant_id,
            Lead.qualified_at.isnot(None),
            Lead.created_at >= start,
        )
    )
    rows = result.all()
    if not rows:
        return {"average_hours": 0.0}

    total = 0.0
    count = 0
    by_source: dict[str, list[float]] = {}
    for created_at, qualified_at, source in rows:
        diff_h = (qualified_at - created_at).total_seconds() / 3600
        total += diff_h
        count += 1
        key = source or "unknown"
        by_source.setdefault(key, []).append(diff_h)

    out = {"average_hours": round(total / count, 2)}
    for source, values in by_source.items():
        out[f"source:{source}"] = round(sum(values) / len(values), 2)
    return out
