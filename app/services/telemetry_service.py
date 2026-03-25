from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox_event import OutboxEvent
from app.models.telemetry_metric import TelemetryMetric


async def record_event_lag(db: AsyncSession, tenant_id: UUID, event_created_at: datetime, processed_at: datetime | None = None) -> None:
    processed = processed_at or datetime.now(timezone.utc)
    lag_ms = int((processed - event_created_at).total_seconds() * 1000)
    db.add(
        TelemetryMetric(
            tenant_id=tenant_id,
            metric_name="event_lag_ms",
            value={"lag_ms": lag_ms},
        )
    )
    await db.flush()


async def record_cadence_send(db: AsyncSession, tenant_id: UUID, success: bool) -> None:
    db.add(
        TelemetryMetric(
            tenant_id=tenant_id,
            metric_name="cadence_send",
            value={"success": success},
        )
    )
    await db.flush()


async def outbox_failure_rate(db: AsyncSession, tenant_id: UUID) -> float:
    total_result = await db.execute(
        select(func.count(OutboxEvent.id)).where(OutboxEvent.tenant_id == tenant_id)
    )
    total = total_result.scalar() or 0
    if total == 0:
        return 0.0

    failed_result = await db.execute(
        select(func.count(OutboxEvent.id)).where(
            OutboxEvent.tenant_id == tenant_id,
            OutboxEvent.publish_error.isnot(None),
        )
    )
    failed = failed_result.scalar() or 0
    return round((failed / total) * 100, 2)
