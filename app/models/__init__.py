"""
CRM Corven — Models package.

Import all models here so Alembic and SQLAlchemy can discover them.
"""

from app.models.agent_log import AgentLog
from app.models.automation import AutomationRule
from app.models.campaign import Campaign
from app.models.broker_config import BrokerConfig
from app.models.conversation_state import ConversationState
from app.models.document import Document
from app.models.event import Event
from app.models.lead import Lead, LeadInteraction, LeadNote
from app.models.lead_cadence import LeadCadence
from app.models.lead_qualification import LeadQualification
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import OTPCode, User
from app.models.whatsapp import Message, WhatsAppInstance
from app.models.outbox_event import OutboxEvent
from app.models.processed_event import ProcessedEvent
from app.models.message_template import MessageTemplate
from app.models.escalation_alert import EscalationAlert
from app.models.telemetry_metric import TelemetryMetric

__all__ = [
    "AgentLog",
    "AutomationRule",
    "Campaign",
    "BrokerConfig",
    "ConversationState",
    "Document",
    "Event",
    "Lead",
    "LeadInteraction",
    "LeadNote",
    "LeadCadence",
    "LeadQualification",
    "Message",
    "OTPCode",
    "OutboxEvent",
    "ProcessedEvent",
    "MessageTemplate",
    "EscalationAlert",
    "TelemetryMetric",
    "Task",
    "Tenant",
    "User",
    "WhatsAppInstance",
]
