from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker_config import BrokerConfig
from app.models.lead import Lead
from app.services.routing_service import route_lead


async def apply_dynamic_sla(db: AsyncSession, tenant_id: UUID, lead: Lead) -> bool:
    if not lead.assigned_to:
        return False

    config_result = await db.execute(
        select(BrokerConfig).where(
            BrokerConfig.tenant_id == tenant_id,
            BrokerConfig.user_id == lead.assigned_to,
            BrokerConfig.is_active == True,
        )
    )
    config = config_result.scalar_one_or_none()
    if not config:
        return False

    threshold = datetime.now(timezone.utc) - timedelta(minutes=config.sla_minutes)
    if lead.updated_at > threshold:
        return False

    lead.priority_score = (lead.priority_score or 0) + 10
    lead.metadata_extra = {**(lead.metadata_extra or {}), "sla_breach": True}
    await route_lead(db, tenant_id, lead, segment=(lead.metadata_extra or {}).get("segment"))
    await db.flush()
    return True
