from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.models.lead_cadence import CadenceStatus, LeadCadence

CADENCE_STEPS: list[tuple[int, str]] = [
    (0, "cadence_d0"),
    (2, "cadence_d2"),
    (5, "cadence_d5"),
    (10, "cadence_d10"),
    (20, "cadence_d20"),
]


async def ensure_cadence(db: AsyncSession, tenant_id: UUID, lead_id: UUID) -> LeadCadence:
    result = await db.execute(
        select(LeadCadence).where(
            LeadCadence.tenant_id == tenant_id,
            LeadCadence.lead_id == lead_id,
        )
    )
    cadence = result.scalar_one_or_none()
    if cadence:
        return cadence

    cadence = LeadCadence(
        tenant_id=tenant_id,
        lead_id=lead_id,
        step=0,
        status=CadenceStatus.ACTIVE,
        next_run_at=datetime.now(timezone.utc),
    )
    db.add(cadence)
    await db.flush()
    await db.refresh(cadence)
    return cadence


def step_payload(step: int, lead: Lead) -> tuple[str, datetime | None]:
    if step >= len(CADENCE_STEPS):
        return "", None

    day_offset, template_key = CADENCE_STEPS[step]
    next_step_index = step + 1
    if next_step_index >= len(CADENCE_STEPS):
        next_run = None
    else:
        next_day = CADENCE_STEPS[next_step_index][0]
        wait_days = max(next_day - day_offset, 0)
        next_run = datetime.now(timezone.utc) + timedelta(days=wait_days)
    return template_key, next_run


async def stop_cadence(db: AsyncSession, tenant_id: UUID, lead_id: UUID, reason: str) -> None:
    result = await db.execute(
        select(LeadCadence).where(
            LeadCadence.tenant_id == tenant_id,
            LeadCadence.lead_id == lead_id,
        )
    )
    cadence = result.scalar_one_or_none()
    if not cadence:
        return
    cadence.status = CadenceStatus.PAUSED
    cadence.context = {**(cadence.context or {}), "paused_reason": reason}
    await db.flush()


async def resume_cadence(db: AsyncSession, tenant_id: UUID, lead_id: UUID) -> LeadCadence | None:
    result = await db.execute(
        select(LeadCadence).where(
            LeadCadence.tenant_id == tenant_id,
            LeadCadence.lead_id == lead_id,
        )
    )
    cadence = result.scalar_one_or_none()
    if not cadence:
        return None
    cadence.status = CadenceStatus.ACTIVE
    cadence.next_run_at = datetime.now(timezone.utc)
    cadence.context = {**(cadence.context or {}), "paused_reason": None}
    await db.flush()
    return cadence
