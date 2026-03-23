"""
CRM Corven — Meta (Official) WhatsApp API provider.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings
from app.modules.whatsapp.providers.base import WhatsAppProvider

settings = get_settings()

META_API_URL = "https://graph.facebook.com/v21.0"


class MetaProvider(WhatsAppProvider):
    """WhatsApp provider using Meta Official API."""

    def __init__(self):
        self.api_token = settings.META_WHATSAPP_TOKEN
        self.phone_id = settings.META_WHATSAPP_PHONE_ID

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def connect(self, instance_name: str, config: dict) -> dict[str, Any]:
        """Meta API doesn't require connection — returns status."""
        return {
            "status": "connected",
            "provider": "meta",
            "phone_id": self.phone_id,
        }

    async def disconnect(self, instance_name: str) -> dict[str, Any]:
        """Meta API doesn't require disconnection."""
        return {"status": "disconnected", "provider": "meta"}

    async def get_status(self, instance_name: str) -> str:
        """Check if Meta API is reachable."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{META_API_URL}/{self.phone_id}",
                    headers=self._headers(),
                )
                response.raise_for_status()
                return "connected"
        except Exception:
            return "disconnected"

    async def send_message(
        self, instance_name: str, to: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send a message via Meta Official API."""
        async with httpx.AsyncClient(timeout=30) as client:
            if media_url:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "image",
                    "image": {"link": media_url, "caption": content or ""},
                }
            else:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "text",
                    "text": {"body": content},
                }

            response = await client.post(
                f"{META_API_URL}/{self.phone_id}/messages",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def process_webhook(self, payload: dict) -> dict[str, Any]:
        """Parse a Meta API webhook payload."""
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])

        if not messages:
            return {}

        msg = messages[0]
        return {
            "external_id": msg.get("id"),
            "from_number": msg.get("from"),
            "instance_name": value.get("metadata", {}).get("display_phone_number"),
            "content": msg.get("text", {}).get("body", ""),
            "media_url": None,
            "direction": "inbound",
            "timestamp": msg.get("timestamp"),
        }
