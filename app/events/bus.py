from __future__ import annotations

import asyncio
import json
import logging

import redis.asyncio as redis

from app.config import get_settings
from app.events.schemas import SalesEvent

logger = logging.getLogger(__name__)
settings = get_settings()
EVENT_STREAM = "corven:sales:events"


class EventBus:
    def __init__(self) -> None:
        self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def publish(self, event: SalesEvent) -> None:
        payload = event.model_dump(mode="json")
        await self._client.xadd(EVENT_STREAM, {"event": json.dumps(payload)})
        logger.info("sales_event_published", extra={"event_name": event.name, "lead_id": event.lead_id})


_bus = EventBus()


def publish_event(event: SalesEvent) -> None:
    asyncio.create_task(_bus.publish(event))
