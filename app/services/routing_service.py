from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.broker_config import BrokerConfig
from app.models.lead import Lead
from app.models.user import User


def _score_bucket(score: int | None) -> str:
    s = score or 0
    if s >= 80:
        return "hot"
    if s >= 50:
        return "warm"
    return "cold"


async def route_lead(db: AsyncSession, tenant_id: UUID, lead: Lead, segment: str | None = None) -> UUID | None:
    bucket = _score_bucket(lead.score)

    users_result = await db.execute(
        select(BrokerConfig, User)
        .join(User, BrokerConfig.user_id == User.id)
        .where(
            BrokerConfig.tenant_id == tenant_id,
            BrokerConfig.is_active == True,
            User.role == "user",
            User.is_active == True,
        )
    )
    candidates = users_result.all()
    if not candidates:
        return None

    best_user_id: UUID | None = None
    best_rank: tuple[int, int, int] | None = None

    for cfg, user in candidates:
        skills = set(cfg.skills or [])
        segments = {s for s in skills if s in {"PF", "PME", "PJ"}}
        capacity = int(cfg.max_capacity)
        sla_priority = max(1, 1440 - int(cfg.sla_minutes))

        if skills and bucket not in skills:
            continue
        if segment and segments and segment not in segments:
            continue

        assigned_result = await db.execute(
            select(func.count(Lead.id)).where(
                Lead.tenant_id == tenant_id,
                Lead.assigned_to == user.id,
                Lead.stage.notin_(["fechado", "perdido"]),
            )
        )
        load = assigned_result.scalar() or 0
        available = max(capacity - load, 0)
        rank = (available, sla_priority, -load)

        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_user_id = user.id

    if best_user_id:
        lead.assigned_to = best_user_id
        await db.flush()

        # Keep active lead count in sync for selected broker
        selected_cfg_result = await db.execute(
            select(BrokerConfig).where(
                BrokerConfig.tenant_id == tenant_id,
                BrokerConfig.user_id == best_user_id,
            )
        )
        selected_cfg = selected_cfg_result.scalar_one_or_none()
        if selected_cfg:
            active_count_result = await db.execute(
                select(func.count(Lead.id)).where(
                    Lead.tenant_id == tenant_id,
                    Lead.assigned_to == best_user_id,
                    Lead.stage.notin_(["fechado", "perdido"]),
                )
            )
            selected_cfg.active_leads = active_count_result.scalar() or 0
            await db.flush()
    return best_user_id
