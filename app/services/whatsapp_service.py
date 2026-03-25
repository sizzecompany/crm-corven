from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.whatsapp import Message, WhatsAppInstance
from app.modules.whatsapp.providers import get_provider


class WhatsAppDeliveryError(RuntimeError):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True)
async def send_message(
    db: AsyncSession,
    tenant_id: UUID,
    phone: str,
    content: str,
    lead_id: UUID | None = None,
    instance_id: UUID | None = None,
) -> Message:
    if instance_id:
        query = select(WhatsAppInstance).where(
            WhatsAppInstance.id == instance_id,
            WhatsAppInstance.tenant_id == tenant_id,
        )
    else:
        query = (
            select(WhatsAppInstance)
            .where(WhatsAppInstance.tenant_id == tenant_id)
            .order_by(WhatsAppInstance.created_at.asc())
            .limit(1)
        )

    result = await db.execute(query)
    instance = result.scalar_one_or_none()
    if not instance:
        raise WhatsAppDeliveryError("No WhatsApp instance configured")

    provider = get_provider(instance.provider)
    provider_result = await provider.send_message(instance.instance_name, phone, content)

    message = Message(
        tenant_id=tenant_id,
        instance_id=instance.id,
        lead_id=lead_id,
        direction="outbound",
        content=content,
        status="sent",
        external_id=str(provider_result.get("id") or provider_result.get("key", {}).get("id", "")),
        metadata_extra={"phone": phone},
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message
