"""
CRM Corven — AI Agent module.

Intelligent agent that can perform CRM actions, query leads,
create tasks, summarize conversations, and interact with the system.
"""

from __future__ import annotations

import time
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from openai import AsyncOpenAI
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.permissions import Role
from app.database import get_db
from app.dependencies import CurrentUser
from app.models.agent_log import AgentLog
from app.models.lead import Lead, LeadStage
from app.models.task import Task

settings = get_settings()


# ── Schemas ──────────────────────────────────────────────────────────────────

class AgentQuery(BaseModel):
    message: str
    context: dict | None = None  # Optional extra context


class AgentResponse(BaseModel):
    response: str
    actions_taken: list[dict] = []
    suggestions: list[str] = []


class AgentLogOut(BaseModel):
    id: str
    action: str
    input_data: dict | None = None
    output_data: dict | None = None
    status: str
    execution_time_ms: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Agent Tools (CRM Actions) ───────────────────────────────────────────────

AGENT_SYSTEM_PROMPT = """Você é a Secretária IA do CRM Corven, especializada em ajudar corretores de planos de saúde.

Suas capacidades:
- Consultar leads e seus status no pipeline
- Sugerir follow-ups para leads parados
- Resumir conversas e interações
- Criar tarefas e lembretes
- Fornecer insights sobre performance
- Ajudar com estratégias de vendas

Sempre responda em português brasileiro. Seja proativa e sugira ações quando possível.
Respeite as permissões do usuário — não acesse dados de outros tenants.
"""


async def get_lead_summary(db: AsyncSession, tenant_id: UUID) -> str:
    """Get a summary of leads for the agent context."""
    result = await db.execute(
        select(Lead.stage, func.count(Lead.id))
        .where(Lead.tenant_id == tenant_id)
        .group_by(Lead.stage)
    )
    stages = {row[0]: row[1] for row in result.all()}

    total = sum(stages.values())
    summary_parts = [f"Total de leads: {total}"]
    for stage in LeadStage:
        count = stages.get(stage.value, 0)
        summary_parts.append(f"  - {stage.value}: {count}")

    return "\n".join(summary_parts)


async def get_pending_tasks_summary(db: AsyncSession, tenant_id: UUID, user_id: UUID) -> str:
    """Get pending tasks for context."""
    result = await db.execute(
        select(Task)
        .where(
            Task.tenant_id == tenant_id,
            Task.assigned_to == user_id,
            Task.status == "pending",
        )
        .limit(10)
    )
    tasks = result.scalars().all()
    if not tasks:
        return "Nenhuma tarefa pendente."

    lines = ["Tarefas pendentes:"]
    for t in tasks:
        due = t.due_date.strftime("%d/%m/%Y") if t.due_date else "sem prazo"
        lines.append(f"  - {t.title} (prazo: {due})")
    return "\n".join(lines)


async def process_agent_query(
    db: AsyncSession, tenant_id: UUID, user_id: UUID, role: str, message: str
) -> AgentResponse:
    """Process a query through the AI agent."""
    start_time = time.time()
    actions_taken = []
    suggestions = []

    # Build context
    lead_summary = await get_lead_summary(db, tenant_id)
    tasks_summary = await get_pending_tasks_summary(db, tenant_id, user_id)

    context = f"""
Contexto atual do CRM:
{lead_summary}

{tasks_summary}

Role do usuário: {role}
"""

    # Call LLM
    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        completion = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "system", "content": context},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=1500,
        )
        response_text = completion.choices[0].message.content or "Sem resposta."
        status = "success"
    except Exception as e:
        response_text = f"Erro ao processar consulta com IA: {str(e)}"
        status = "error"

    execution_time = int((time.time() - start_time) * 1000)

    # Log the action
    log = AgentLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action="query",
        input_data={"message": message},
        output_data={"response": response_text[:500]},
        status=status,
        execution_time_ms=execution_time,
    )
    db.add(log)
    await db.flush()

    return AgentResponse(
        response=response_text,
        actions_taken=actions_taken,
        suggestions=suggestions,
    )


# ── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/agent", tags=["AI Agent"])


@router.post("/query", response_model=AgentResponse)
async def query_agent(
    body: AgentQuery,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Interact with the AI agent."""
    return await process_agent_query(
        db, current_user.tenant_id, current_user.id,
        current_user.role, body.message,
    )


@router.get("/logs", response_model=list[AgentLogOut])
async def get_agent_logs(
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get AI agent action logs."""
    query = select(AgentLog).where(AgentLog.tenant_id == current_user.tenant_id)
    if Role(current_user.role) == Role.USER:
        query = query.where(AgentLog.user_id == current_user.id)
    result = await db.execute(
        query.order_by(AgentLog.created_at.desc()).offset(skip).limit(limit)
    )
    return [
        AgentLogOut(
            id=str(l.id), action=l.action, input_data=l.input_data,
            output_data=l.output_data, status=l.status,
            execution_time_ms=l.execution_time_ms, created_at=l.created_at,
        )
        for l in result.scalars().all()
    ]
