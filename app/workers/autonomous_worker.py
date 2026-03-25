from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select

from app.agents.crew_orchestrator import apply_qualification_progress
from app.cadence.engine import ensure_cadence, resume_cadence, step_payload, stop_cadence
from app.database import AsyncSessionLocal
from app.events.bus import EVENT_STREAM, EventBus
from app.events.outbox import outbox_to_sales_event
from app.events.schemas import EventName, SalesEvent
from app.models.conversation_state import ConversationState
from app.models.lead import Lead, LeadInteraction, LeadStage
from app.models.lead_cadence import CadenceStatus, LeadCadence
from app.models.lead_qualification import LeadQualification, QualificationStatus
from app.models.outbox_event import OutboxEvent
from app.models.processed_event import ProcessedEvent
from app.models.whatsapp import Message
from app.services.routing_service import route_lead
from app.services.sla_service import apply_dynamic_sla
from app.services.scoring_service import compute_score, update_priority_score
from app.services.escalation_service import maybe_escalate_hot_lead
from app.services.telemetry_service import record_cadence_send, record_event_lag
from app.services.template_engine import render_message, track_template_outcome
from app.services.whatsapp_service import WhatsAppDeliveryError, send_message
from app.workers.automation_worker import celery_app
from app.automation.reactivation_engine import run_reactivation_playbook

logger = logging.getLogger(__name__)

AUTO_RESPONSE_TEMPLATE = (
    "Olá {{name}}, vi que você demonstrou interesse em plano de saúde. "
    "Posso te fazer 2 perguntas rápidas para te indicar a melhor opção?"
)


class EventAlreadyProcessed(Exception):
    pass


def _human_like_reply(content: str) -> bool:
    text = (content or "").strip().lower()
    if not text:
        return False
    if any(word in text for word in ["sim", "quero", "interesse", "pode", "oi", "bom dia", "vamos"]):
        return True
    return len(text.split()) >= 3


async def _mark_processed(db, tenant_id: UUID, event: SalesEvent) -> None:
    existing = await db.execute(select(ProcessedEvent).where(ProcessedEvent.event_id == event.id))
    if existing.scalar_one_or_none():
        raise EventAlreadyProcessed(event.id)

    db.add(
        ProcessedEvent(
            tenant_id=tenant_id,
            event_id=event.id,
            event_name=event.name,
        )
    )
    await db.flush()


@celery_app.task(name="app.workers.autonomous_worker.event_processor")
def event_processor(event_data: dict):
    async def _run():
        async with AsyncSessionLocal() as db:
            event = SalesEvent(**event_data)
            tenant_id = UUID(event.tenant_id)

            try:
                await _mark_processed(db, tenant_id, event)
            except EventAlreadyProcessed:
                await db.rollback()
                return

            if event.name == EventName.LEAD_CREATED and event.lead_id:
                lead = await db.get(Lead, UUID(event.lead_id))
                if not lead:
                    await db.commit()
                    return

                persona = (event.payload.get("segment") or "PF").upper()
                content, version = await render_message(
                    db,
                    tenant_id,
                    "auto_response",
                    persona,
                    {"name": lead.name},
                )
                if not content:
                    content = AUTO_RESPONSE_TEMPLATE.replace("{{name}}", lead.name)
                    version = "A"
                try:
                    msg = await send_message(db, tenant_id=tenant_id, phone=lead.phone or "", content=content, lead_id=lead.id)
                except WhatsAppDeliveryError as exc:
                    logger.warning("auto_response_skipped", extra={"lead_id": str(lead.id), "error": str(exc)})
                    msg = None

                db.add(
                    LeadInteraction(
                        lead_id=lead.id,
                        tenant_id=tenant_id,
                        type="whatsapp",
                        content="Auto-response sent" if msg else "Auto-response failed: missing instance",
                    )
                )

                await ensure_cadence(db, tenant_id, lead.id)

                qual_result = await db.execute(
                    select(LeadQualification).where(
                        LeadQualification.tenant_id == tenant_id,
                        LeadQualification.lead_id == lead.id,
                    )
                )
                qual = qual_result.scalar_one_or_none()
                if not qual:
                    db.add(
                        LeadQualification(
                            tenant_id=tenant_id,
                            lead_id=lead.id,
                            status=QualificationStatus.ACTIVE,
                            current_question_index=0,
                        )
                    )

                await route_lead(db, tenant_id, lead, segment=event.payload.get("segment"))
                await update_priority_score(db, tenant_id, lead)

                if msg:
                    if not lead.first_response_at:
                        lead.first_response_at = msg.created_at
                    lead.metadata_extra = {**(lead.metadata_extra or {}), "auto_response_version": version}
                    celery_app.send_task(
                        "app.workers.autonomous_worker.agent_runner",
                        args=[event.tenant_id, str(lead.id), str(msg.id)],
                        countdown=1,
                    )

            elif event.name == EventName.MESSAGE_RECEIVED and event.lead_id and event.message_id:
                lead = await db.get(Lead, UUID(event.lead_id))
                message = await db.get(Message, UUID(event.message_id))
                if not lead or not message:
                    await db.commit()
                    return

                if _human_like_reply(message.content or ""):
                    version = (lead.metadata_extra or {}).get("auto_response_version")
                    segment = ((lead.metadata_extra or {}).get("segment") or "PF").upper()
                    if version:
                        await track_template_outcome(db, tenant_id, "auto_response", segment, version, "reply")
                    await stop_cadence(db, tenant_id, lead.id, "lead_responded")
                    if lead.stage == LeadStage.NOVO.value:
                        lead.stage = LeadStage.CONTATO_INICIADO.value

                    celery_app.send_task(
                        "app.workers.autonomous_worker.agent_runner",
                        args=[event.tenant_id, str(lead.id), str(message.id)],
                        countdown=1,
                    )

                await update_priority_score(db, tenant_id, lead)
                await apply_dynamic_sla(db, tenant_id, lead)
                await maybe_escalate_hot_lead(db, tenant_id=tenant_id, lead=lead)

            elif event.name == EventName.LEAD_QUALIFIED and event.lead_id:
                lead = await db.get(Lead, UUID(event.lead_id))
                qual_result = await db.execute(
                    select(LeadQualification).where(
                        LeadQualification.tenant_id == tenant_id,
                        LeadQualification.lead_id == UUID(event.lead_id),
                    )
                )
                qual = qual_result.scalar_one_or_none()
                if lead and qual:
                    score, reason = compute_score(qual)
                    lead.score = score
                    lead.score_reason = reason
                    lead.stage = "qualified"
                    lead.qualified_at = datetime.now(timezone.utc)
                    await route_lead(db, tenant_id, lead, segment=qual.plan_type)
                    await resume_cadence(db, tenant_id, lead.id)
                    await update_priority_score(db, tenant_id, lead)

            elif event.name == EventName.LEAD_RESPONDED and event.lead_id:
                await stop_cadence(db, tenant_id, UUID(event.lead_id), "lead_responded")

            await record_event_lag(db, tenant_id, event.created_at)
            await db.commit()

    asyncio.run(_run())


@celery_app.task(name="app.workers.autonomous_worker.agent_runner")
def agent_runner(tenant_id: str, lead_id: str, message_id: str):
    async def _run():
        async with AsyncSessionLocal() as db:
            tenant_uuid = UUID(tenant_id)
            lead_uuid = UUID(lead_id)
            msg_uuid = UUID(message_id)

            lead = await db.get(Lead, lead_uuid)
            message = await db.get(Message, msg_uuid)
            if not lead or not message:
                return

            qual_result = await db.execute(
                select(LeadQualification).where(
                    LeadQualification.tenant_id == tenant_uuid,
                    LeadQualification.lead_id == lead_uuid,
                )
            )
            qualification = qual_result.scalar_one_or_none()
            if not qualification:
                qualification = LeadQualification(
                    tenant_id=tenant_uuid,
                    lead_id=lead_uuid,
                    status=QualificationStatus.ACTIVE,
                    current_question_index=0,
                )
                db.add(qualification)
                await db.flush()

            history_result = await db.execute(
                select(Message)
                .where(Message.tenant_id == tenant_uuid, Message.lead_id == lead_uuid)
                .order_by(Message.created_at.asc())
            )
            history = "\n".join([f"{m.direction}: {m.content}" for m in history_result.scalars().all() if m.content])

            conversation_result = await db.execute(
                select(ConversationState).where(
                    ConversationState.tenant_id == tenant_uuid,
                    ConversationState.lead_id == lead_uuid,
                )
            )
            convo = conversation_result.scalar_one_or_none()
            if not convo:
                convo = ConversationState(tenant_id=tenant_uuid, lead_id=lead_uuid, memory={})
                db.add(convo)

            qualification, next_question = await apply_qualification_progress(
                db,
                qualification,
                latest_message=message.content or "",
                history=history,
            )

            convo.last_message_id = msg_uuid
            convo.memory = {**(convo.memory or {}), "last_question_index": qualification.current_question_index}

            if qualification.status == QualificationStatus.QUALIFIED:
                celery_app.send_task(
                    "app.workers.autonomous_worker.event_processor",
                    args=[
                        SalesEvent(
                            name=EventName.LEAD_QUALIFIED,
                            tenant_id=tenant_id,
                            lead_id=lead_id,
                            message_id=message_id,
                            payload={},
                        ).model_dump(mode="json")
                    ],
                    countdown=1,
                )
            elif next_question:
                try:
                    await send_message(db, tenant_uuid, lead.phone or "", next_question, lead_id=lead_uuid)
                except WhatsAppDeliveryError:
                    logger.warning("qualification_question_not_sent", extra={"lead_id": lead_id})

            await db.commit()

    asyncio.run(_run())


@celery_app.task(name="app.workers.autonomous_worker.cadence_scheduler")
def cadence_scheduler():
    async def _run():
        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(LeadCadence, Lead)
                .join(Lead, LeadCadence.lead_id == Lead.id)
                .where(
                    LeadCadence.status == CadenceStatus.ACTIVE,
                    LeadCadence.next_run_at.is_not(None),
                    LeadCadence.next_run_at <= now,
                )
                .limit(500)
            )
            rows = result.all()

            for cadence, lead in rows:
                content, next_run = step_payload(cadence.step, lead)
                if not content:
                    cadence.status = CadenceStatus.COMPLETED
                    cadence.next_run_at = None
                    continue

                try:
                    persona = ((lead.metadata_extra or {}).get("segment") or "PF").upper()
                    template_key = content
                    rendered, version = await render_message(
                        db,
                        lead.tenant_id,
                        template_key,
                        persona,
                        {"name": lead.name},
                    )
                    if not rendered:
                        rendered = f"Olá {lead.name}, seguimos disponíveis para apoiar sua decisão."
                    await send_message(db, lead.tenant_id, lead.phone or "", rendered, lead_id=lead.id)
                    await record_cadence_send(db, lead.tenant_id, True)
                except WhatsAppDeliveryError:
                    await record_cadence_send(db, lead.tenant_id, False)
                    continue

                cadence.last_sent_at = now
                cadence.step += 1
                cadence.next_run_at = next_run
                if next_run is None:
                    cadence.status = CadenceStatus.COMPLETED

                # reactivation playbook checkpoints (30/60/90 days idle)
                if lead.updated_at <= now - timedelta(days=30):
                    cadence.context = {**(cadence.context or {}), "reactivation_30": True}
                    await run_reactivation_playbook(
                        db,
                        tenant_id=lead.tenant_id,
                        lead_id=lead.id,
                        phone=lead.phone or "",
                        name=lead.name,
                        plan_type=(lead.metadata_extra or {}).get("segment"),
                        day_window=30,
                    )
                if lead.updated_at <= now - timedelta(days=60):
                    cadence.context = {**(cadence.context or {}), "reactivation_60": True}
                    await run_reactivation_playbook(
                        db,
                        tenant_id=lead.tenant_id,
                        lead_id=lead.id,
                        phone=lead.phone or "",
                        name=lead.name,
                        plan_type=(lead.metadata_extra or {}).get("segment"),
                        day_window=60,
                    )
                if lead.updated_at <= now - timedelta(days=90):
                    cadence.context = {**(cadence.context or {}), "reactivation_90": True}
                    await run_reactivation_playbook(
                        db,
                        tenant_id=lead.tenant_id,
                        lead_id=lead.id,
                        phone=lead.phone or "",
                        name=lead.name,
                        plan_type=(lead.metadata_extra or {}).get("segment"),
                        day_window=90,
                    )

                await update_priority_score(db, lead.tenant_id, lead)
                await apply_dynamic_sla(db, lead.tenant_id, lead)
                await maybe_escalate_hot_lead(db, tenant_id=lead.tenant_id, lead=lead)

            await db.commit()

    asyncio.run(_run())


@celery_app.task(name="app.workers.autonomous_worker.publish_outbox_events")
def publish_outbox_events(batch_size: int = 100):
    async def _run():
        async with AsyncSessionLocal() as db:
            bus = EventBus()
            result = await db.execute(
                select(OutboxEvent)
                .where(OutboxEvent.published == False)
                .order_by(OutboxEvent.created_at.asc())
                .limit(batch_size)
            )
            items = result.scalars().all()

            for item in items:
                event = outbox_to_sales_event(item)
                try:
                    await bus.publish(event)
                    item.published = True
                    item.publish_error = None
                    item.published_at = datetime.now(timezone.utc)
                except Exception as exc:  # pragma: no cover
                    item.publish_error = str(exc)

            await db.commit()

    asyncio.run(_run())


@celery_app.task(name="app.workers.autonomous_worker.consume_event_stream")
def consume_event_stream(max_events: int = 50):
    async def _run():
        bus = EventBus()
        last_id_key = "corven:sales:events:last_id"
        last_id = await bus._client.get(last_id_key) or "0-0"
        records = await bus._client.xread({EVENT_STREAM: last_id}, count=max_events, block=1000)
        for _, items in records:
            for message_id, payload in items:
                raw = payload.get("event")
                if not raw:
                    continue
                event_processor.delay(json.loads(raw))
                await bus._client.set(last_id_key, message_id)

    asyncio.run(_run())
