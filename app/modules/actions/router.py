from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.lead import Lead
from app.models.lead_cadence import LeadCadence
from app.models.task import Task
from app.models.escalation_alert import EscalationAlert
from app.services.kpi_service import (
    conversion_rate,
    cost_per_conversion_by_source,
    first_response_time_seconds,
    qualification_rate,
    time_to_qualification_hours,
)
from app.services.telemetry_service import outbox_failure_rate


class NextActionOut(BaseModel):
    lead_id: str
    lead_name: str
    action_type: str
    action_label: str
    due_at: datetime | None = None
    priority_score: float | None = 0


class NextActionsResponse(BaseModel):
    actions: list[NextActionOut]
    kpis: dict[str, float]


router = APIRouter(tags=["Next Actions"])


@router.get("/next-activities", response_model=NextActionsResponse)
async def next_activities(
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    actions: list[NextActionOut] = []

    cadence_result = await db.execute(
        select(LeadCadence, Lead)
        .join(Lead, LeadCadence.lead_id == Lead.id)
        .where(
            LeadCadence.tenant_id == current_user.tenant_id,
            LeadCadence.status == "active",
        )
        .order_by(LeadCadence.next_run_at.asc().nullslast())
        .limit(limit)
    )
    for cadence, lead in cadence_result.all():
        actions.append(
            NextActionOut(
                lead_id=str(lead.id),
                lead_name=lead.name,
                action_type="cadence",
                action_label=f"Executar passo {cadence.step + 1} da cadência",
                due_at=cadence.next_run_at,
                priority_score=lead.priority_score,
            )
        )

    task_result = await db.execute(
        select(Task, Lead)
        .join(Lead, Task.lead_id == Lead.id)
        .where(
            Task.tenant_id == current_user.tenant_id,
            Task.status == "pending",
            Task.assigned_to == current_user.id,
        )
        .order_by(Task.due_date.asc().nullslast())
        .limit(limit)
    )
    for task, lead in task_result.all():
        actions.append(
            NextActionOut(
                lead_id=str(lead.id),
                lead_name=lead.name,
                action_type="task",
                action_label=task.title,
                due_at=task.due_date,
                priority_score=lead.priority_score,
            )
        )

    actions.sort(key=lambda x: (-(x.priority_score or 0), x.due_at or datetime.max))
    escalation_result = await db.execute(
        select(EscalationAlert, Lead)
        .join(Lead, EscalationAlert.lead_id == Lead.id)
        .where(
            EscalationAlert.tenant_id == current_user.tenant_id,
            EscalationAlert.resolved_at.is_(None),
        )
        .order_by(EscalationAlert.created_at.desc())
        .limit(20)
    )
    for alert, lead in escalation_result.all():
        actions.insert(
            0,
            NextActionOut(
                lead_id=str(lead.id),
                lead_name=lead.name,
                action_type="escalation",
                action_label=f"URGENTE: {alert.reason}",
                due_at=alert.created_at,
                priority_score=(lead.priority_score or 0) + 100,
            ),
        )

    actions = actions[:limit]

    kpis = {
        "first_response_time_seconds": await first_response_time_seconds(db, current_user.tenant_id),
        "qualification_rate": await qualification_rate(db, current_user.tenant_id),
        "conversion_rate": await conversion_rate(db, current_user.tenant_id),
        "outbox_failure_rate": await outbox_failure_rate(db, current_user.tenant_id),
    }
    cost_per_conv = await cost_per_conversion_by_source(db, current_user.tenant_id)
    t2q = await time_to_qualification_hours(db, current_user.tenant_id)
    kpis.update({f"cost_per_conversion:{k}": v for k, v in cost_per_conv.items()})
    kpis.update({f"time_to_qualification:{k}": v for k, v in t2q.items()})
    return NextActionsResponse(actions=actions, kpis=kpis)
