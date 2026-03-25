from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

from pydantic import BaseModel, Field


class EventName:
    LEAD_CREATED = "lead.created"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    LEAD_IDLE = "lead.idle"
    LEAD_RESPONDED = "lead.responded"
    LEAD_QUALIFIED = "lead.qualified"


class SalesEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tenant_id: str
    lead_id: str | None = None
    message_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
