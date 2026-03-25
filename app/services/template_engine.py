from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message_template import MessageTemplate
from app.services.template_service import render_template

DEFAULT_TEMPLATES = {
    "auto_response": {
        "PF": {
            "A": "Olá {{name}}, vi seu interesse em plano de saúde. Posso fazer 2 perguntas rápidas para te indicar a melhor opção?",
            "B": "Oi {{name}}! Obrigado pelo contato. Em 2 perguntas eu já te mostro o melhor plano para seu perfil.",
        },
        "PME": {
            "A": "Olá {{name}}, posso mapear rapidamente o plano ideal para sua empresa?",
            "B": "Oi {{name}}, em 2 perguntas te mostro cenários para PME com melhor custo-benefício.",
        },
        "PJ": {
            "A": "Olá {{name}}, posso te ajudar com opções empresariais para CNPJ?",
            "B": "Oi {{name}}, vamos comparar opções de plano empresarial em poucos minutos?",
        },
    },
    "reactivation_30": {
        "PF": {"A": "{{name}}, ainda quer retomar sua cotação? Posso simular agora."},
        "PME": {"A": "{{name}}, temos novas condições para PME. Quer simular agora?"},
        "PJ": {"A": "{{name}}, reabrimos análise para plano empresarial. Quer falar com especialista?"},
    },
    "reactivation_60": {
        "PF": {"A": "{{name}}, condição limitada disponível hoje. Deseja retomar?"},
        "PME": {"A": "{{name}}, oportunidade de redução de custo para sua empresa. Posso te mostrar?"},
        "PJ": {"A": "{{name}}, atualizamos cenários PJ. Quer rever com consultor?"},
    },
    "reactivation_90": {
        "PF": {"A": "Última chamada, {{name}}: ainda deseja seu plano?"},
        "PME": {"A": "{{name}}, último contato para reativar proposta PME. Vamos fechar um cenário?"},
        "PJ": {"A": "{{name}}, última janela para retomada empresarial com suporte dedicado."},
    },
    "cadence_d0": {
        "PF": {"A": "{{name}}, posso te ajudar a escolher o melhor plano de saúde hoje?"},
        "PME": {"A": "{{name}}, posso mapear o melhor cenário para sua PME hoje?"},
        "PJ": {"A": "{{name}}, posso comparar opções empresariais para sua operação?"},
    },
    "cadence_d2": {
        "PF": {"A": "{{name}}, passando para lembrar: quer simular as melhores opções?"},
        "PME": {"A": "{{name}}, quer que eu traga uma simulação PME atualizada?"},
        "PJ": {"A": "{{name}}, posso te enviar uma simulação PJ com opções estratégicas?"},
    },
    "cadence_d5": {
        "PF": {"A": "{{name}}, ainda consigo condições especiais hoje. Posso te explicar?"},
        "PME": {"A": "{{name}}, ainda temos janela com condição comercial para PME."},
        "PJ": {"A": "{{name}}, temos condição empresarial ativa por tempo limitado."},
    },
    "cadence_d10": {
        "PF": {"A": "{{name}}, último contato desta rodada. Ainda faz sentido cotar agora?"},
        "PME": {"A": "{{name}}, encerrando rodada de propostas PME. Deseja retomar?"},
        "PJ": {"A": "{{name}}, encerrando rodada PJ. Quer reabrir com especialista?"},
    },
    "cadence_d20": {
        "PF": {"A": "{{name}}, posso reativar sua cotação agora em 1 minuto."},
        "PME": {"A": "{{name}}, reabrimos simulação PME. Quer ver os novos números?"},
        "PJ": {"A": "{{name}}, retomamos comparação PJ com suporte dedicado. Avançamos?"},
    },
}


async def get_template_variant(
    db: AsyncSession,
    tenant_id: UUID,
    template_key: str,
    persona: str,
) -> tuple[str, str]:
    result = await db.execute(
        select(MessageTemplate)
        .where(
            MessageTemplate.tenant_id == tenant_id,
            MessageTemplate.template_key == template_key,
            MessageTemplate.persona == persona,
        )
        .order_by(MessageTemplate.sent_count.asc())
    )
    records = result.scalars().all()
    if records:
        template = records[0]
        template.sent_count += 1
        await db.flush()
        return template.content, template.version

    defaults = DEFAULT_TEMPLATES.get(template_key, {}).get(persona) or DEFAULT_TEMPLATES.get(template_key, {}).get("PF")
    if not defaults:
        return "", "A"

    # A/B lightweight rotation based on count parity from available variants
    variant = "A" if len(records) % 2 == 0 else "B"
    if variant not in defaults:
        variant = list(defaults.keys())[0]
    return defaults[variant], variant


async def render_message(
    db: AsyncSession,
    tenant_id: UUID,
    template_key: str,
    persona: str,
    context: dict,
) -> tuple[str, str]:
    template, version = await get_template_variant(db, tenant_id, template_key, persona)
    if not template:
        return "", version
    return render_template(template, context), version


async def track_template_outcome(
    db: AsyncSession,
    tenant_id: UUID,
    template_key: str,
    persona: str,
    version: str,
    outcome: str,
) -> None:
    result = await db.execute(
        select(MessageTemplate).where(
            MessageTemplate.tenant_id == tenant_id,
            MessageTemplate.template_key == template_key,
            MessageTemplate.persona == persona,
            MessageTemplate.version == version,
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        return

    if outcome == "reply":
        template.reply_count += 1
    elif outcome == "convert":
        template.conversion_count += 1
    await db.flush()
