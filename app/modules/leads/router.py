"""
CRM Corven — Leads (CRM Kanban) module: schemas, service, router.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.permissions import Action, Resource, Role
from app.database import get_db
from app.dependencies import CurrentUser, require_resource_permission
from app.models.lead import Lead, LeadInteraction, LeadNote, LeadStage
from app.models.task import Task
from app.events.outbox import enqueue_outbox_event
from app.events.schemas import EventName


class LeadCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=100)
    campaign_id: str | None = None
    assigned_to: str | None = None
    metadata_extra: dict | None = None


class LeadUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    source: str | None = Field(default=None, max_length=100)
    assigned_to: str | None = None
    metadata_extra: dict | None = None
    score: int | None = Field(default=None, ge=0, le=100)


class LeadStageUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: LeadStage


class LeadOut(BaseModel):
    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    stage: str
    source: str | None = None
    campaign_id: str | None = None
    assigned_to: str | None = None
    score: int | None = 0
    score_reason: str | None = None
    priority_score: float | None = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InteractionOut(BaseModel):
    id: str
    type: str
    content: str | None = None
    created_by: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str = Field(min_length=1, max_length=2000)


class NoteOut(BaseModel):
    id: str
    content: str
    created_by: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    due_date: datetime | None = None
    assigned_to: str | None = None
    is_follow_up: bool = False


class TaskOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: str
    assigned_to: str | None = None
    is_follow_up: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ActionCompleteRequest(BaseModel):
    action_type: str  # task | cadence
    task_id: str | None = None


async def list_leads(
    db: AsyncSession,
    tenant_id: UUID,
    stage: str | None = None,
    source: str | None = None,
    assigned_to: UUID | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Lead]:
    query = select(Lead).where(Lead.tenant_id == tenant_id)
    if stage:
        query = query.where(Lead.stage == stage)
    if source:
        query = query.where(Lead.source == source)
    if assigned_to:
        query = query.where(Lead.assigned_to == assigned_to)
    query = query.order_by(Lead.updated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_lead(db: AsyncSession, tenant_id: UUID, lead_id: UUID) -> Lead:
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
    )
    lead = result.scalar_one_or_none()
    if lead is None:
        raise NotFoundError("Lead", str(lead_id))
    return lead


async def create_lead(db: AsyncSession, tenant_id: UUID, user_id: UUID, data: LeadCreate) -> Lead:
    lead = Lead(
        tenant_id=tenant_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        source=data.source,
        campaign_id=UUID(data.campaign_id) if data.campaign_id else None,
        assigned_to=UUID(data.assigned_to) if data.assigned_to else user_id,
        metadata_extra=data.metadata_extra or {},
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    interaction = LeadInteraction(
        lead_id=lead.id,
        tenant_id=tenant_id,
        type="system",
        content="Lead criado",
        created_by=user_id,
    )
    db.add(interaction)
    await db.flush()

    return lead


async def update_lead(db: AsyncSession, tenant_id: UUID, lead_id: UUID, data: LeadUpdate) -> Lead:
    lead = await get_lead(db, tenant_id, lead_id)
    update_data = data.model_dump(exclude_unset=True)
    if "assigned_to" in update_data and update_data["assigned_to"]:
        update_data["assigned_to"] = UUID(update_data["assigned_to"])
    for field, value in update_data.items():
        setattr(lead, field, value)
    await db.flush()
    await db.refresh(lead)
    return lead


async def update_lead_stage(
    db: AsyncSession, tenant_id: UUID, lead_id: UUID, stage: str, user_id: UUID
) -> Lead:
    lead = await get_lead(db, tenant_id, lead_id)
    old_stage = lead.stage
    lead.stage = stage
    await db.flush()

    interaction = LeadInteraction(
        lead_id=lead.id,
        tenant_id=tenant_id,
        type="stage_change",
        content=f"Estágio alterado: {old_stage} → {stage}",
        created_by=user_id,
    )
    db.add(interaction)
    await db.flush()
    await db.refresh(lead)
    return lead


async def get_interactions(db: AsyncSession, tenant_id: UUID, lead_id: UUID) -> list[LeadInteraction]:
    await get_lead(db, tenant_id, lead_id)
    result = await db.execute(
        select(LeadInteraction)
        .where(LeadInteraction.lead_id == lead_id, LeadInteraction.tenant_id == tenant_id)
        .order_by(LeadInteraction.created_at.desc())
    )
    return list(result.scalars().all())


async def add_note(db: AsyncSession, tenant_id: UUID, lead_id: UUID, user_id: UUID, content: str) -> LeadNote:
    await get_lead(db, tenant_id, lead_id)
    note = LeadNote(
        lead_id=lead_id,
        tenant_id=tenant_id,
        content=content,
        created_by=user_id,
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    return note


async def add_task(
    db: AsyncSession, tenant_id: UUID, lead_id: UUID, user_id: UUID, data: TaskCreate
) -> Task:
    await get_lead(db, tenant_id, lead_id)
    task = Task(
        tenant_id=tenant_id,
        lead_id=lead_id,
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        assigned_to=UUID(data.assigned_to) if data.assigned_to else user_id,
        is_follow_up=data.is_follow_up,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


router = APIRouter(prefix="/leads", tags=["CRM / Leads"])


def _lead_out(l: Lead) -> LeadOut:
    return LeadOut(
        id=str(l.id), name=l.name, email=l.email, phone=l.phone,
        stage=l.stage, source=l.source,
        campaign_id=str(l.campaign_id) if l.campaign_id else None,
        assigned_to=str(l.assigned_to) if l.assigned_to else None,
        score=l.score, score_reason=l.score_reason, priority_score=l.priority_score,
        created_at=l.created_at, updated_at=l.updated_at,
    )


@router.get("/", response_model=list[LeadOut])
async def list_leads_endpoint(
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.READ),
    stage: LeadStage | None = Query(None),
    source: str | None = Query(None, max_length=100),
    assigned_to: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    user_filter = None
    if Role(current_user.role) == Role.USER:
        user_filter = current_user.id

    leads = await list_leads(
        db,
        current_user.tenant_id,
        stage=stage.value if stage else None,
        source=source,
        assigned_to=user_filter or (UUID(assigned_to) if assigned_to else None),
        skip=skip,
        limit=limit,
    )
    return [_lead_out(l) for l in leads]


@router.post("/", response_model=LeadOut, status_code=201)
async def create_lead_endpoint(
    body: LeadCreate,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.CREATE),
    db: AsyncSession = Depends(get_db),
):
    lead = await create_lead(db, current_user.tenant_id, current_user.id, body)
    await enqueue_outbox_event(
        db,
        tenant_id=current_user.tenant_id,
        event_name=EventName.LEAD_CREATED,
        payload={
            "lead_id": str(lead.id),
            "source": lead.source,
            "segment": (lead.metadata_extra or {}).get("segment", "PF"),
        },
        aggregate_id=str(lead.id),
        dedupe_key=f"lead-created:{lead.id}",
    )
    return _lead_out(lead)


@router.get("/priority", response_model=list[LeadOut])
async def list_leads_by_priority(
    current_user: CurrentUser,
    _permission=require_resource_permission(Resource.LEADS, Action.READ),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Lead)
        .where(Lead.tenant_id == current_user.tenant_id)
        .order_by(Lead.priority_score.desc().nullslast(), Lead.updated_at.desc())
        .limit(limit)
    )
    return [_lead_out(l) for l in result.scalars().all()]


@router.get("/{lead_id}", response_model=LeadOut)
async def get_lead_endpoint(
    lead_id: UUID,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.READ),
    db: AsyncSession = Depends(get_db),
):
    lead = await get_lead(db, current_user.tenant_id, lead_id)
    return _lead_out(lead)


@router.patch("/{lead_id}", response_model=LeadOut)
async def update_lead_endpoint(
    lead_id: UUID,
    body: LeadUpdate,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.UPDATE),
    db: AsyncSession = Depends(get_db),
):
    lead = await update_lead(db, current_user.tenant_id, lead_id, body)
    return _lead_out(lead)


@router.patch("/{lead_id}/stage", response_model=LeadOut)
async def update_lead_stage_endpoint(
    lead_id: UUID,
    body: LeadStageUpdate,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.UPDATE),
    db: AsyncSession = Depends(get_db),
):
    lead = await update_lead_stage(db, current_user.tenant_id, lead_id, body.stage.value, current_user.id)
    return _lead_out(lead)


@router.get("/{lead_id}/interactions", response_model=list[InteractionOut])
async def get_lead_interactions(
    lead_id: UUID,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.READ),
    db: AsyncSession = Depends(get_db),
):
    interactions = await get_interactions(db, current_user.tenant_id, lead_id)
    return [
        InteractionOut(
            id=str(i.id), type=i.type, content=i.content,
            created_by=str(i.created_by) if i.created_by else None,
            created_at=i.created_at,
        )
        for i in interactions
    ]


@router.post("/{lead_id}/notes", response_model=NoteOut, status_code=201)
async def add_lead_note(
    lead_id: UUID,
    body: NoteCreate,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.UPDATE),
    db: AsyncSession = Depends(get_db),
):
    note = await add_note(db, current_user.tenant_id, lead_id, current_user.id, body.content)
    return NoteOut(
        id=str(note.id), content=note.content,
        created_by=str(note.created_by) if note.created_by else None,
        created_at=note.created_at,
    )


@router.post("/{lead_id}/tasks", response_model=TaskOut, status_code=201)
async def add_lead_task(
    lead_id: UUID,
    body: TaskCreate,
    current_user: CurrentUser,
    _permission= require_resource_permission(Resource.LEADS, Action.UPDATE),
    db: AsyncSession = Depends(get_db),
):
    task = await add_task(db, current_user.tenant_id, lead_id, current_user.id, body)
    return TaskOut(
        id=str(task.id), title=task.title, description=task.description,
        due_date=task.due_date, status=task.status,
        assigned_to=str(task.assigned_to) if task.assigned_to else None,
        is_follow_up=task.is_follow_up, created_at=task.created_at,
    )


@router.post("/{lead_id}/action-complete")
async def complete_action(
    lead_id: UUID,
    body: ActionCompleteRequest,
    current_user: CurrentUser,
    _permission=require_resource_permission(Resource.LEADS, Action.UPDATE),
    db: AsyncSession = Depends(get_db),
):
    await get_lead(db, current_user.tenant_id, lead_id)
    if body.action_type == "task" and body.task_id:
        task_result = await db.execute(
            select(Task).where(
                Task.id == UUID(body.task_id),
                Task.tenant_id == current_user.tenant_id,
                Task.lead_id == lead_id,
            )
        )
        task = task_result.scalar_one()
        task.status = "done"
        await db.flush()
        return {"status": "ok", "action": "task_completed"}

    if body.action_type == "cadence":
        from app.models.lead_cadence import LeadCadence

        cadence_result = await db.execute(
            select(LeadCadence).where(
                LeadCadence.tenant_id == current_user.tenant_id,
                LeadCadence.lead_id == lead_id,
            )
        )
        cadence = cadence_result.scalar_one_or_none()
        if cadence:
            cadence.status = "paused"
            await db.flush()
        return {"status": "ok", "action": "cadence_paused"}

    if body.action_type == "escalation":
        from app.models.escalation_alert import EscalationAlert
        from datetime import timezone

        alert_result = await db.execute(
            select(EscalationAlert).where(
                EscalationAlert.tenant_id == current_user.tenant_id,
                EscalationAlert.lead_id == lead_id,
                EscalationAlert.resolved_at.is_(None),
            )
        )
        alert = alert_result.scalar_one_or_none()
        if alert:
            alert.resolved_at = datetime.now(timezone.utc)
            await db.flush()
        return {"status": "ok", "action": "escalation_resolved"}

    return {"status": "ignored"}
