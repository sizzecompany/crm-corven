"""
CRM Corven — Calendar / Agenda module.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import CurrentUser
from app.models.event import Event


# ── Schemas ──────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime | None = None
    all_day: bool = False
    location: str | None = None
    lead_id: str | None = None
    reminder_minutes: int = 30


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    all_day: bool | None = None
    location: str | None = None
    reminder_minutes: int | None = None


class EventOut(BaseModel):
    id: str
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime | None = None
    all_day: bool
    location: str | None = None
    lead_id: str | None = None
    user_id: str
    reminder_minutes: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Service ──────────────────────────────────────────────────────────────────

async def list_events(
    db: AsyncSession, tenant_id: UUID, user_id: UUID | None = None,
    from_date: datetime | None = None, skip: int = 0, limit: int = 50
) -> list[Event]:
    query = select(Event).where(Event.tenant_id == tenant_id)
    if user_id:
        query = query.where(Event.user_id == user_id)
    if from_date:
        query = query.where(Event.start_datetime >= from_date)
    result = await db.execute(
        query.order_by(Event.start_datetime.asc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create_event(db: AsyncSession, tenant_id: UUID, user_id: UUID, data: EventCreate) -> Event:
    event = Event(
        tenant_id=tenant_id,
        user_id=user_id,
        title=data.title,
        description=data.description,
        start_datetime=data.start_datetime,
        end_datetime=data.end_datetime,
        all_day=data.all_day,
        location=data.location,
        lead_id=UUID(data.lead_id) if data.lead_id else None,
        reminder_minutes=data.reminder_minutes,
    )
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


async def update_event(db: AsyncSession, tenant_id: UUID, event_id: UUID, data: EventUpdate) -> Event:
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.tenant_id == tenant_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise NotFoundError("Event", str(event_id))

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    await db.flush()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, tenant_id: UUID, event_id: UUID) -> None:
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.tenant_id == tenant_id)
    )
    event = result.scalar_one_or_none()
    if event is None:
        raise NotFoundError("Event", str(event_id))
    await db.delete(event)
    await db.flush()


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/calendar", tags=["Calendar / Agenda"])


def _out(e: Event) -> EventOut:
    return EventOut(
        id=str(e.id), title=e.title, description=e.description,
        start_datetime=e.start_datetime, end_datetime=e.end_datetime,
        all_day=e.all_day, location=e.location,
        lead_id=str(e.lead_id) if e.lead_id else None,
        user_id=str(e.user_id), reminder_minutes=e.reminder_minutes,
        created_at=e.created_at,
    )


@router.get("/", response_model=list[EventOut])
async def list_events_endpoint(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    events = await list_events(db, current_user.tenant_id, current_user.id)
    return [_out(e) for e in events]


@router.get("/upcoming", response_model=list[EventOut])
async def upcoming_events(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get upcoming events from now."""
    events = await list_events(
        db, current_user.tenant_id, current_user.id,
        from_date=datetime.now(timezone.utc),
    )
    return [_out(e) for e in events]


@router.post("/", response_model=EventOut, status_code=201)
async def create_event_endpoint(
    body: EventCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    event = await create_event(db, current_user.tenant_id, current_user.id, body)
    return _out(event)


@router.patch("/{event_id}", response_model=EventOut)
async def update_event_endpoint(
    event_id: UUID,
    body: EventUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    event = await update_event(db, current_user.tenant_id, event_id, body)
    return _out(event)


@router.delete("/{event_id}", status_code=204)
async def delete_event_endpoint(
    event_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    await delete_event(db, current_user.tenant_id, event_id)
