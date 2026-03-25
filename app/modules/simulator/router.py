from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.lead import Lead
from app.models.lead_qualification import LeadQualification
from app.services.simulator_service import estimate_plan
from app.events.outbox import enqueue_outbox_event


class EstimateOut(BaseModel):
    tiers: list[dict]
    cta: str


router = APIRouter(prefix="/simulator", tags=["Simulator"])


@router.post("/{lead_id}/estimate", response_model=EstimateOut)
async def estimate(
    lead_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    lead_result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == current_user.tenant_id)
    )
    lead = lead_result.scalar_one()

    qual_result = await db.execute(
        select(LeadQualification).where(
            LeadQualification.lead_id == lead_id,
            LeadQualification.tenant_id == current_user.tenant_id,
        )
    )
    qualification = qual_result.scalar_one_or_none()

    estimate_result = estimate_plan(
        age=qualification.age if qualification else None,
        plan_type=qualification.plan_type if qualification else None,
        has_dependents=qualification.has_dependents if qualification else None,
        urgency=qualification.urgency if qualification else None,
    )

    lead.metadata_extra = {
        **(lead.metadata_extra or {}),
        "last_simulation": {
            "tiers": estimate_result.tiers,
        },
    }

    await enqueue_outbox_event(
        db,
        tenant_id=current_user.tenant_id,
        event_name="simulator.estimate.created",
        payload={"lead_id": str(lead_id), "tiers": estimate_result.tiers},
        aggregate_id=str(lead_id),
        dedupe_key=f"simulator:{lead_id}:{estimate_result.tiers[0]['monthly_price']}",
    )

    await db.flush()
    return EstimateOut(
        tiers=estimate_result.tiers,
        cta=estimate_result.cta,
    )
