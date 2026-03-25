from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.lead_qualification import LeadQualification
from app.models.whatsapp import Message


def compute_score(qualification: LeadQualification) -> tuple[int, str]:
    if (
        qualification.urgency == "high"
        and (qualification.age or 0) > 30
        and bool(qualification.has_dependents)
    ):
        return 90, "Hot lead: urgency alta, idade > 30 e possui dependentes"

    if qualification.age and qualification.city and qualification.plan_type and qualification.urgency:
        return 65, "Warm lead: qualificação completa sem sinais de urgência alta"

    return 30, "Cold lead: baixa urgência ou qualificação incompleta"


async def update_priority_score(db: AsyncSession, tenant_id: UUID, lead: Lead) -> float:
    now = datetime.now(timezone.utc)

    engagement_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.tenant_id == tenant_id,
            Message.lead_id == lead.id,
            Message.direction == "inbound",
        )
    )
    engagement = engagement_result.scalar() or 0

    qual_result = await db.execute(
        select(LeadQualification).where(
            LeadQualification.tenant_id == tenant_id,
            LeadQualification.lead_id == lead.id,
        )
    )
    qual = qual_result.scalar_one_or_none()
    qualification_level = 1.0 if qual and qual.status == "qualified" else 0.4 if qual else 0.1

    recency_hours = max((now - lead.updated_at).total_seconds() / 3600, 1)
    recency_factor = max(0.2, 1 / recency_hours)

    response_time_factor = 1.0 if engagement > 0 else 0.2

    priority_score = (
        (lead.score or 0) * 0.45
        + min(engagement, 10) * 3.0
        + qualification_level * 20
        + response_time_factor * 10
        + recency_factor * 15
    )
    lead.priority_score = round(priority_score, 2)
    await db.flush()
    return lead.priority_score
