from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.escalation_alert import EscalationAlert
from app.models.lead import Lead


async def maybe_escalate_hot_lead(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    lead: Lead,
    hours_without_response: int = 4,
) -> bool:
    if (lead.score or 0) < 80:
        return False

    threshold = datetime.now(timezone.utc) - timedelta(hours=hours_without_response)
    if lead.updated_at > threshold:
        return False

    existing = await db.execute(
        select(EscalationAlert).where(
            EscalationAlert.tenant_id == tenant_id,
            EscalationAlert.lead_id == lead.id,
            EscalationAlert.resolved_at.is_(None),
        )
    )
    if existing.scalar_one_or_none():
        return False

    db.add(
        EscalationAlert(
            tenant_id=tenant_id,
            lead_id=lead.id,
            reason="hot_lead_no_response",
            level="critical",
            metadata_extra={"hours_without_response": hours_without_response},
        )
    )
    lead.priority_score = (lead.priority_score or 0) + 15
    await db.flush()
    return True
