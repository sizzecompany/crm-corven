"""
CRM Corven — WhatsApp provider abstraction layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WhatsAppProvider(ABC):
    """Base class for WhatsApp providers (Evolution API, Meta API)."""

    @abstractmethod
    async def connect(self, instance_name: str, config: dict) -> dict[str, Any]:
        """Connect/create a WhatsApp instance."""
        ...

    @abstractmethod
    async def disconnect(self, instance_name: str) -> dict[str, Any]:
        """Disconnect a WhatsApp instance."""
        ...

    @abstractmethod
    async def get_status(self, instance_name: str) -> str:
        """Get the connection status of an instance."""
        ...

    @abstractmethod
    async def send_message(
        self, instance_name: str, to: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send a message to a phone number."""
        ...

    @abstractmethod
    async def process_webhook(self, payload: dict) -> dict[str, Any]:
        """Process an incoming webhook payload and return parsed message data."""
        ...
