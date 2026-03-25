from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.schemas import SalesEvent
from app.models.outbox_event import OutboxEvent


async def enqueue_outbox_event(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    event_name: str,
    payload: dict,
    aggregate_id: str | None,
    dedupe_key: str,
) -> OutboxEvent:
    existing = await db.execute(select(OutboxEvent).where(OutboxEvent.dedupe_key == dedupe_key))
    outbox = existing.scalar_one_or_none()
    if outbox:
        return outbox

    outbox = OutboxEvent(
        tenant_id=tenant_id,
        event_name=event_name,
        payload=payload,
        aggregate_id=aggregate_id,
        dedupe_key=dedupe_key,
        published=False,
    )
    db.add(outbox)
    await db.flush()
    return outbox


def outbox_to_sales_event(outbox: OutboxEvent) -> SalesEvent:
    payload = outbox.payload or {}
    return SalesEvent(
        id=str(outbox.id),
        name=outbox.event_name,
        tenant_id=str(outbox.tenant_id),
        lead_id=payload.get("lead_id"),
        message_id=payload.get("message_id"),
        payload=payload,
        created_at=datetime.now(timezone.utc),
    )
