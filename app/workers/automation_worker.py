"""
CRM Corven — Celery automation worker.

Handles background automation rules:
- Lead idle detection → create tasks
- New message notifications
- Lead stage follow-ups
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from celery import Celery
import sentry_sdk
from sqlalchemy import select, func
from sentry_sdk.integrations.celery import CeleryIntegration

from app.config import get_settings

settings = get_settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[CeleryIntegration()],
    )

celery_app = Celery(
    "crm_corven",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        "check-idle-leads": {
            "task": "app.workers.automation_worker.check_idle_leads",
            "schedule": 3600.0,  # Every hour
        },
        "check-overdue-tasks": {
            "task": "app.workers.automation_worker.check_overdue_tasks",
            "schedule": 1800.0,  # Every 30 minutes
        },
        "consume-sales-events": {
            "task": "app.workers.autonomous_worker.consume_event_stream",
            "schedule": 2.0,
        },
        "publish-outbox-events": {
            "task": "app.workers.autonomous_worker.publish_outbox_events",
            "schedule": 1.0,
        },
        "run-cadence-scheduler": {
            "task": "app.workers.autonomous_worker.cadence_scheduler",
            "schedule": 60.0,
        },
    },
)


@celery_app.task(name="app.workers.automation_worker.check_idle_leads")
def check_idle_leads():
    """Check for leads that have been idle for configured period and create tasks."""
    from app.database import AsyncSessionLocal
    from app.models.automation import AutomationRule
    from app.models.lead import Lead
    from app.models.task import Task

    async def _run():
        async with AsyncSessionLocal() as db:
            # Get all active automation rules with 'lead_idle' trigger
            result = await db.execute(
                select(AutomationRule).where(
                    AutomationRule.trigger == "lead_idle",
                    AutomationRule.is_active == True,
                )
            )
            rules = result.scalars().all()

            for rule in rules:
                idle_days = rule.conditions.get("idle_days", 3)
                threshold = datetime.now(timezone.utc) - timedelta(days=idle_days)

                # Find idle leads for this tenant
                leads_result = await db.execute(
                    select(Lead).where(
                        Lead.tenant_id == rule.tenant_id,
                        Lead.updated_at < threshold,
                        Lead.stage.notin_(["fechado", "perdido"]),
                    )
                )
                idle_leads = leads_result.scalars().all()

                for lead in idle_leads:
                    action_type = rule.actions.get("type", "create_task")
                    if action_type == "create_task":
                        task = Task(
                            tenant_id=rule.tenant_id,
                            lead_id=lead.id,
                            title=rule.actions.get("title", f"Follow-up: {lead.name}"),
                            description=f"Lead parado há {idle_days} dias. Automação: {rule.name}",
                            assigned_to=lead.assigned_to,
                            is_follow_up=True,
                        )
                        db.add(task)

                rule.last_run_at = datetime.now(timezone.utc)

            await db.commit()

    asyncio.run(_run())
    return {"status": "completed"}


@celery_app.task(name="app.workers.automation_worker.check_overdue_tasks")
def check_overdue_tasks():
    """Check for overdue tasks and create notifications."""
    # TODO: Implement notification system
    return {"status": "completed"}


@celery_app.task(name="app.workers.automation_worker.process_new_lead")
def process_new_lead(tenant_id: str, lead_id: str):
    """Process automation rules triggered by new lead creation."""
    from app.database import AsyncSessionLocal
    from app.models.automation import AutomationRule
    from app.models.task import Task

    async def _run():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(AutomationRule).where(
                    AutomationRule.tenant_id == tenant_id,
                    AutomationRule.trigger == "lead_created",
                    AutomationRule.is_active == True,
                )
            )
            rules = result.scalars().all()

            for rule in rules:
                action_type = rule.actions.get("type", "create_task")
                if action_type == "create_task":
                    task = Task(
                        tenant_id=tenant_id,
                        lead_id=lead_id,
                        title=rule.actions.get("title", "Contatar novo lead"),
                        description=f"Automação: {rule.name}",
                        is_follow_up=True,
                    )
                    db.add(task)

            await db.commit()

    asyncio.run(_run())
    return {"status": "completed"}


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    name="app.workers.automation_worker.process_new_message",
)
def process_new_message(self, tenant_id: str, message_id: str):
    """Process automation rules triggered by new WhatsApp message."""
    # TODO: Notify user, create interaction, etc.
    return {"status": "completed"}


# Registers autonomous sales tasks in the same Celery app namespace.
from app.workers import autonomous_worker  # noqa: E402,F401
