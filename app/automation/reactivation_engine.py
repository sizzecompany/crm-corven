from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.template_engine import render_message
from app.services.whatsapp_service import send_message

PLAYBOOKS = {
    30: "reactivation_30",
    60: "reactivation_60",
    90: "reactivation_90",
}


def persona_from_plan_type(plan_type: str | None) -> str:
    if plan_type == "business":
        return "PJ"
    if plan_type in {"family", "pme"}:
        return "PME"
    return "PF"


async def run_reactivation_playbook(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    lead_id: UUID,
    phone: str,
    name: str,
    plan_type: str | None,
    day_window: int,
) -> bool:
    template_key = PLAYBOOKS.get(day_window)
    if not template_key:
        return False

    persona = persona_from_plan_type(plan_type)
    content, version = await render_message(
        db,
        tenant_id=tenant_id,
        template_key=template_key,
        persona=persona,
        context={"name": name},
    )
    if not content:
        return False

    await send_message(db, tenant_id=tenant_id, phone=phone, content=content, lead_id=lead_id)
    return True
