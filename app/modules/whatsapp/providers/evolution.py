"""
CRM Corven — Evolution API WhatsApp provider.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings
from app.modules.whatsapp.providers.base import WhatsAppProvider

settings = get_settings()


class EvolutionProvider(WhatsAppProvider):
    """WhatsApp provider using Evolution API (unofficial)."""

    def __init__(self):
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY

    def _headers(self) -> dict:
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    async def connect(self, instance_name: str, config: dict) -> dict[str, Any]:
        """Create and connect an Evolution API instance."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/instance/create",
                headers=self._headers(),
                json={
                    "instanceName": instance_name,
                    "qrcode": True,
                    "integration": "WHATSAPP-BAILEYS",
                    **config,
                },
            )
            response.raise_for_status()
            return response.json()

    async def disconnect(self, instance_name: str) -> dict[str, Any]:
        """Disconnect an Evolution API instance."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.delete(
                f"{self.base_url}/instance/logout/{instance_name}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_status(self, instance_name: str) -> str:
        """Get connection status of an Evolution API instance."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/instance/connectionState/{instance_name}",
                headers=self._headers(),
            )
            response.raise_for_status()
            data = response.json()
            return data.get("instance", {}).get("state", "disconnected")

    async def send_message(
        self, instance_name: str, to: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send a text or media message via Evolution API."""
        async with httpx.AsyncClient(timeout=30) as client:
            if media_url:
                response = await client.post(
                    f"{self.base_url}/message/sendMedia/{instance_name}",
                    headers=self._headers(),
                    json={
                        "number": to,
                        "mediatype": "image",
                        "media": media_url,
                        "caption": content or "",
                    },
                )
            else:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{instance_name}",
                    headers=self._headers(),
                    json={
                        "number": to,
                        "text": content,
                    },
                )
            response.raise_for_status()
            return response.json()

    async def process_webhook(self, payload: dict) -> dict[str, Any]:
        """Parse an Evolution API webhook payload."""
        data = payload.get("data", {})
        message_data = data.get("message", {})

        return {
            "external_id": data.get("key", {}).get("id"),
            "from_number": data.get("key", {}).get("remoteJid", "").split("@")[0],
            "instance_name": payload.get("instance"),
            "content": message_data.get("conversation")
            or message_data.get("extendedTextMessage", {}).get("text", ""),
            "media_url": None,
            "direction": "inbound",
            "timestamp": data.get("messageTimestamp"),
        }
