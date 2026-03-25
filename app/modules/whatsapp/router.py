"""
CRM Corven — WhatsApp module: router + service.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.models.whatsapp import Message, WhatsAppInstance
from app.modules.whatsapp.providers import get_provider
from app.events.outbox import enqueue_outbox_event
from app.events.schemas import EventName


# ── Schemas ──────────────────────────────────────────────────────────────────

class InstanceCreate(BaseModel):
    provider: str  # "evolution" or "meta"
    instance_name: str
    phone_number: str | None = None
    config: dict = {}


class InstanceOut(BaseModel):
    id: str
    provider: str
    instance_name: str
    phone_number: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    instance_id: str
    to: str
    content: str
    media_url: str | None = None
    lead_id: str | None = None


class MessageOut(BaseModel):
    id: str
    direction: str
    content: str | None = None
    media_url: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Service ──────────────────────────────────────────────────────────────────

async def create_instance(db: AsyncSession, tenant_id: UUID, data: InstanceCreate) -> WhatsAppInstance:
    provider = get_provider(data.provider)
    connect_result = await provider.connect(data.instance_name, data.config)

    instance = WhatsAppInstance(
        tenant_id=tenant_id,
        provider=data.provider,
        instance_name=data.instance_name,
        phone_number=data.phone_number,
        status=connect_result.get("status", "connecting"),
        config=data.config,
    )
    db.add(instance)
    await db.flush()
    await db.refresh(instance)
    return instance


async def get_instance(db: AsyncSession, tenant_id: UUID, instance_id: UUID) -> WhatsAppInstance:
    result = await db.execute(
        select(WhatsAppInstance).where(
            WhatsAppInstance.id == instance_id,
            WhatsAppInstance.tenant_id == tenant_id,
        )
    )
    instance = result.scalar_one_or_none()
    if instance is None:
        raise NotFoundError("WhatsApp Instance", str(instance_id))
    return instance


async def get_instance_status(db: AsyncSession, tenant_id: UUID, instance_id: UUID) -> str:
    instance = await get_instance(db, tenant_id, instance_id)
    provider = get_provider(instance.provider)
    status = await provider.get_status(instance.instance_name)
    instance.status = status
    await db.flush()
    return status


async def send_message(
    db: AsyncSession, tenant_id: UUID, data: SendMessageRequest
) -> Message:
    instance = await get_instance(db, tenant_id, UUID(data.instance_id))
    provider = get_provider(instance.provider)

    result = await provider.send_message(
        instance.instance_name, data.to, data.content, data.media_url
    )

    message = Message(
        tenant_id=tenant_id,
        instance_id=instance.id,
        lead_id=UUID(data.lead_id) if data.lead_id else None,
        direction="outbound",
        content=data.content,
        media_url=data.media_url,
        status="sent",
        external_id=str(result.get("key", {}).get("id", "")),
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def process_webhook_message(
    db: AsyncSession, provider_name: str, payload: dict
) -> Message | None:
    """Process incoming webhook and store message."""
    provider = get_provider(provider_name)
    parsed = await provider.process_webhook(payload)

    if not parsed or not parsed.get("from_number"):
        return None

    # Find the instance by name
    result = await db.execute(
        select(WhatsAppInstance).where(
            WhatsAppInstance.instance_name == parsed.get("instance_name")
        )
    )
    instance = result.scalar_one_or_none()
    if instance is None:
        return None

    from_number = "".join([c for c in parsed.get("from_number", "") if c.isdigit()])
    lead_id = None
    if from_number:
        from app.models.lead import Lead

        lead_result = await db.execute(
            select(Lead).where(
                Lead.tenant_id == instance.tenant_id,
                Lead.phone.isnot(None),
            )
        )
        for lead in lead_result.scalars().all():
            normalized = "".join([c for c in (lead.phone or "") if c.isdigit()])
            if normalized.endswith(from_number[-10:]):
                lead_id = lead.id
                break

    message = Message(
        tenant_id=instance.tenant_id,
        instance_id=instance.id,
        lead_id=lead_id,
        direction="inbound",
        content=parsed.get("content", ""),
        media_url=parsed.get("media_url"),
        status="received",
        external_id=parsed.get("external_id"),
        metadata_extra={"from_number": parsed.get("from_number")},
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_messages_by_lead(
    db: AsyncSession, tenant_id: UUID, lead_id: UUID, skip: int = 0, limit: int = 100
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.tenant_id == tenant_id, Message.lead_id == lead_id)
        .order_by(Message.created_at.asc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


def _instance_out(i: WhatsAppInstance) -> InstanceOut:
    return InstanceOut(
        id=str(i.id), provider=i.provider, instance_name=i.instance_name,
        phone_number=i.phone_number, status=i.status, created_at=i.created_at,
    )


def _message_out(m: Message) -> MessageOut:
    return MessageOut(
        id=str(m.id), direction=m.direction, content=m.content,
        media_url=m.media_url, status=m.status, created_at=m.created_at,
    )


@router.post("/instances", response_model=InstanceOut, status_code=201)
async def create_instance_endpoint(
    body: InstanceCreate,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    """Connect a new WhatsApp number."""
    instance = await create_instance(db, current_user.tenant_id, body)
    return _instance_out(instance)


@router.get("/instances", response_model=list[InstanceOut])
async def list_instances(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WhatsAppInstance).where(WhatsAppInstance.tenant_id == current_user.tenant_id)
    )
    return [_instance_out(i) for i in result.scalars().all()]


@router.get("/instances/{instance_id}/status")
async def get_instance_status_endpoint(
    instance_id: UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    status = await get_instance_status(db, current_user.tenant_id, instance_id)
    return {"instance_id": str(instance_id), "status": status}


@router.post("/send", response_model=MessageOut)
async def send_message_endpoint(
    body: SendMessageRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Send a WhatsApp message."""
    message = await send_message(db, current_user.tenant_id, body)
    await enqueue_outbox_event(
        db,
        tenant_id=current_user.tenant_id,
        event_name=EventName.MESSAGE_SENT,
        payload={"lead_id": body.lead_id, "message_id": str(message.id), "to": body.to},
        aggregate_id=body.lead_id,
        dedupe_key=f"msg-sent:{message.id}",
    )
    return _message_out(message)


@router.post("/webhook/{provider}")
async def webhook_handler(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive incoming webhook from WhatsApp provider."""
    payload = await request.json()
    message = await process_webhook_message(db, provider, payload)
    if message:
        await enqueue_outbox_event(
            db,
            tenant_id=message.tenant_id,
            event_name=EventName.MESSAGE_RECEIVED,
            payload={
                "lead_id": str(message.lead_id) if message.lead_id else None,
                "message_id": str(message.id),
                "content": message.content or "",
            },
            aggregate_id=str(message.lead_id) if message.lead_id else str(message.id),
            dedupe_key=f"msg-received:{message.external_id or message.id}",
        )
    return {"status": "ok", "message_id": str(message.id) if message else None}


@router.post("/webhook")
async def webhook_handler_default(
    request: Request,
    provider: str = Query("evolution"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()
    message = await process_webhook_message(db, provider, payload)
    if message:
        await enqueue_outbox_event(
            db,
            tenant_id=message.tenant_id,
            event_name=EventName.MESSAGE_RECEIVED,
            payload={
                "lead_id": str(message.lead_id) if message.lead_id else None,
                "message_id": str(message.id),
                "content": message.content or "",
            },
            aggregate_id=str(message.lead_id) if message.lead_id else str(message.id),
            dedupe_key=f"msg-received:{message.external_id or message.id}",
        )
    return {"status": "ok", "message_id": str(message.id) if message else None}


class MessageWithLeadOut(BaseModel):
    id: str
    direction: str
    content: str | None = None
    media_url: str | None = None
    status: str
    lead_id: str | None = None
    lead_name: str | None = None
    lead_phone: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/messages", response_model=list[MessageWithLeadOut])
async def list_all_messages(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get all WhatsApp messages for the tenant (admin view)."""
    from app.models.lead import Lead

    result = await db.execute(
        select(Message, Lead.name, Lead.phone)
        .outerjoin(Lead, Message.lead_id == Lead.id)
        .where(Message.tenant_id == current_user.tenant_id)
        .order_by(Message.created_at.desc())
        .offset(skip).limit(limit)
    )
    rows = result.all()
    return [
        MessageWithLeadOut(
            id=str(m.id), direction=m.direction, content=m.content,
            media_url=m.media_url, status=m.status,
            lead_id=str(m.lead_id) if m.lead_id else None,
            lead_name=name, lead_phone=phone,
            created_at=m.created_at,
        )
        for m, name, phone in rows
    ]


@router.get("/messages/{lead_id}", response_model=list[MessageOut])
async def get_lead_messages(
    lead_id: UUID,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get message history for a lead."""
    messages = await get_messages_by_lead(db, current_user.tenant_id, lead_id, skip, limit)
    return [_message_out(m) for m in messages]
