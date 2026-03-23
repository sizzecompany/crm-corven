"""
CRM Corven — Models package.

Import all models here so Alembic and SQLAlchemy can discover them.
"""

from app.models.agent_log import AgentLog
from app.models.automation import AutomationRule
from app.models.campaign import Campaign
from app.models.document import Document
from app.models.event import Event
from app.models.lead import Lead, LeadInteraction, LeadNote
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import OTPCode, User
from app.models.whatsapp import Message, WhatsAppInstance

__all__ = [
    "AgentLog",
    "AutomationRule",
    "Campaign",
    "Document",
    "Event",
    "Lead",
    "LeadInteraction",
    "LeadNote",
    "Message",
    "OTPCode",
    "Task",
    "Tenant",
    "User",
    "WhatsAppInstance",
]
