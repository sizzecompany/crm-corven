"""
CRM Corven — Comprehensive demo data seed.

Run: python -m app.seed_demo
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.agent_log import AgentLog
from app.models.automation import AutomationRule
from app.models.campaign import Campaign
from app.models.document import Document
from app.models.event import Event
from app.models.lead import Lead, LeadInteraction, LeadNote
from app.models.task import Task
from app.models.tenant import Tenant
from app.models.user import User
from app.models.whatsapp import Message, WhatsAppInstance

now = datetime.now(timezone.utc)


def hours_ago(h):
    return now - timedelta(hours=h)


def days_ago(d):
    return now - timedelta(days=d)


def days_from_now(d):
    return now + timedelta(days=d)


LEAD_NAMES = [
    ("Maria Silva", "maria.silva@gmail.com", "11999001001"),
    ("João Santos", "joao.santos@hotmail.com", "11999002002"),
    ("Ana Oliveira", "ana.oliveira@gmail.com", "21999003003"),
    ("Carlos Souza", "carlos.souza@yahoo.com", "11999004004"),
    ("Fernanda Lima", "fernanda.lima@gmail.com", "31999005005"),
    ("Roberto Almeida", "roberto.almeida@outlook.com", "11999006006"),
    ("Juliana Costa", "juliana.costa@gmail.com", "21999007007"),
    ("Pedro Ferreira", "pedro.ferreira@gmail.com", "11999008008"),
    ("Camila Rodrigues", "camila.rodrigues@hotmail.com", "41999009009"),
    ("Lucas Pereira", "lucas.pereira@gmail.com", "11999010010"),
    ("Beatriz Martins", "beatriz.martins@gmail.com", "21999011011"),
    ("Thiago Gonçalves", "thiago.goncalves@yahoo.com", "11999012012"),
    ("Larissa Barbosa", "larissa.barbosa@gmail.com", "31999013013"),
    ("Rafael Ribeiro", "rafael.ribeiro@outlook.com", "11999014014"),
    ("Patricia Carvalho", "patricia.carvalho@gmail.com", "21999015015"),
    ("Marcelo Araújo", "marcelo.araujo@gmail.com", "11999016016"),
    ("Amanda Nascimento", "amanda.nascimento@hotmail.com", "41999017017"),
    ("Diego Monteiro", "diego.monteiro@gmail.com", "11999018018"),
    ("Isabela Teixeira", "isabela.teixeira@gmail.com", "21999019019"),
    ("Gustavo Mendes", "gustavo.mendes@yahoo.com", "11999020020"),
]

SOURCES = ["whatsapp", "meta_ads", "google_ads", "indicacao", "organic"]

INTERACTIONS = [
    "Lead entrou em contato via WhatsApp perguntando sobre plano familiar.",
    "Ligação realizada. Lead interessado em plano empresarial PME.",
    "Enviado comparativo de planos por email.",
    "Lead respondeu WhatsApp: quer saber sobre carência.",
    "Reunião online feita. Lead pediu proposta formal.",
    "Proposta enviada: Unimed PME 30 vidas.",
    "Follow-up por WhatsApp. Lead disse que vai decidir na semana que vem.",
    "Lead informou que está comparando com Amil.",
    "Nova ligação: lead fechou com outro corretor, mas quer renegociar.",
    "Lead solicitou simulação para plano individual.",
]

NOTES = [
    "Cliente tem 3 dependentes. Preferência por Unimed.",
    "Empresa com 15 funcionários. CNPJ ativo.",
    "Urgência: plano atual vence em 30 dias.",
    "Lead indicado por Maria Silva — dar prioridade.",
    "Interessado em plano com coparticipação.",
    "Já teve Amil, quer mudar por causa do reajuste.",
    "Orçamento máximo: R$ 800/mês por vida.",
    "Precisa de cobertura em São Paulo capital.",
]

TASK_TITLES = [
    "Ligar para o lead",
    "Enviar proposta por email",
    "Follow-up via WhatsApp",
    "Agendar reunião presencial",
    "Enviar comparativo de planos",
    "Verificar documentação do lead",
    "Confirmar dados para contrato",
    "Preparar apresentação personalizada",
]


async def seed_demo():
    async with AsyncSessionLocal() as db:
        # Check existing
        result = await db.execute(select(Lead))
        if result.scalars().first():
            print("⚠️  Limpando dados demo existentes...")
            for model in [AgentLog, Message, WhatsAppInstance, AutomationRule,
                          Document, Event, Task, LeadNote, LeadInteraction, Lead, Campaign]:
                await db.execute(model.__table__.delete())
            await db.flush()

        # Get tenant & users
        tenant = (await db.execute(select(Tenant).limit(1))).scalar_one_or_none()
        if not tenant:
            print("❌ Nenhum tenant encontrado. Execute 'python -m app.seed' primeiro.")
            return

        users = list((await db.execute(
            select(User).where(User.tenant_id == tenant.id)
        )).scalars().all())
        if not users:
            print("❌ Nenhum usuário encontrado.")
            return

        admin_user = next((u for u in users if u.role == "admin"), users[0])
        regular_user = next((u for u in users if u.role == "user"), users[0])
        assignees = [admin_user.id, regular_user.id]

        print(f"📦 Tenant: {tenant.name} (ID: {tenant.id})")

        # ── 1. Campaigns ──────────────────────────────────────────────
        campaigns = []
        for name, source, budget, desc in [
            ("Meta Ads - Plano Familiar Q1", "meta_ads", 5000.0, "Facebook/Instagram focada em famílias"),
            ("Google Ads - PME Saúde", "google_ads", 8000.0, "Google para empresas buscando plano corporativo"),
            ("Indicação Premium", "indicacao", 0.0, "Programa de indicação com bônus"),
        ]:
            c = Campaign(tenant_id=tenant.id, name=name, source=source,
                         budget=budget, description=desc, status="active",
                         created_at=days_ago(random.randint(10, 60)))
            db.add(c)
            campaigns.append(c)
        await db.flush()
        print(f"  ✅ {len(campaigns)} campanhas")

        # ── 2. Leads (20) ────────────────────────────────────────────
        leads = []
        stages = (["novo"] * 4 + ["contato_iniciado"] * 4 + ["em_negociacao"] * 5 +
                  ["aguardando_retorno"] * 3 + ["fechado"] * 3 + ["perdido"] * 1)
        random.shuffle(stages)

        for i, (name, email, phone) in enumerate(LEAD_NAMES):
            lead = Lead(
                tenant_id=tenant.id, name=name, email=email, phone=phone,
                source=random.choice(SOURCES), stage=stages[i],
                assigned_to=random.choice(assignees),
                campaign_id=random.choice(campaigns).id if random.random() > 0.3 else None,
                metadata_extra={"plano_interesse": random.choice(["Individual", "Familiar", "PME", "Empresarial"])},
                created_at=days_ago(random.randint(1, 45)),
            )
            db.add(lead)
            leads.append(lead)
        await db.flush()
        print(f"  ✅ {len(leads)} leads")

        # ── 3. Lead Interactions ──────────────────────────────────────
        ic = 0
        for lead in leads:
            for _ in range(random.randint(1, 4)):
                db.add(LeadInteraction(
                    tenant_id=tenant.id, lead_id=lead.id,
                    type=random.choice(["whatsapp", "phone", "email", "meeting"]),
                    content=random.choice(INTERACTIONS),
                    created_by=random.choice(assignees),
                    created_at=days_ago(random.randint(0, 30)),
                ))
                ic += 1
        await db.flush()
        print(f"  ✅ {ic} interações")

        # ── 4. Lead Notes ─────────────────────────────────────────────
        nc = 0
        for lead in leads:
            if random.random() > 0.4:
                for _ in range(random.randint(1, 3)):
                    db.add(LeadNote(
                        tenant_id=tenant.id, lead_id=lead.id,
                        content=random.choice(NOTES),
                        created_by=random.choice(assignees),
                        created_at=days_ago(random.randint(0, 20)),
                    ))
                    nc += 1
        await db.flush()
        print(f"  ✅ {nc} notas")

        # ── 5. Tasks ──────────────────────────────────────────────────
        tc = 0
        for lead in leads:
            if random.random() > 0.3:
                for _ in range(random.randint(1, 2)):
                    done = random.random() > 0.6
                    db.add(Task(
                        tenant_id=tenant.id, lead_id=lead.id,
                        title=random.choice(TASK_TITLES),
                        description=f"Referente ao lead {lead.name}",
                        assigned_to=random.choice(assignees),
                        due_date=days_from_now(random.randint(-5, 10)),
                        status="done" if done else "pending",
                        is_follow_up=random.choice([True, False]),
                        created_at=days_ago(random.randint(0, 15)),
                    ))
                    tc += 1
        await db.flush()
        print(f"  ✅ {tc} tarefas")

        # ── 6. Calendar Events ────────────────────────────────────────
        events = [
            ("Reunião Maria Silva - Plano Familiar", 2),
            ("Call João Santos - PME", 3),
            ("Follow-up Fernanda Lima", 1),
            ("Treinamento - Novos planos 2026", 5),
            ("Apresentação empresa XYZ", 7),
            ("Revisão metas mensais", 4),
            ("Ligação Carlos Souza - Renovação", -1),
            ("Pipeline review semanal", 0),
        ]
        for title, offset in events:
            db.add(Event(
                tenant_id=tenant.id, user_id=random.choice(assignees),
                title=title, description=f"Evento: {title}",
                start_datetime=days_from_now(offset).replace(hour=random.randint(9, 16)),
                end_datetime=days_from_now(offset).replace(hour=random.randint(10, 18)),
                lead_id=random.choice(leads).id if random.random() > 0.3 else None,
                reminder_minutes=30,
            ))
        await db.flush()
        print(f"  ✅ {len(events)} eventos")

        # ── 7. WhatsApp ───────────────────────────────────────────────
        wa = WhatsAppInstance(
            tenant_id=tenant.id, provider="evolution",
            instance_name="corven-principal", phone_number="5511999888777",
            status="connected", config={"webhook_url": "http://localhost:8000/api/v1/whatsapp/webhook"},
        )
        db.add(wa)
        await db.flush()

        mc = 0
        for lead in random.sample(leads, min(8, len(leads))):
            convos = [
                ("inbound", "Olá, gostaria de informações sobre planos de saúde."),
                ("outbound", f"Olá {lead.name.split()[0]}! Temos ótimas opções. Qual tipo de plano busca?"),
                ("inbound", "Estou procurando um plano familiar para 4 pessoas."),
                ("outbound", "Ótimo! Planos familiares a partir de R$ 450/mês. Posso enviar simulação?"),
                ("inbound", f"Sim! Meu email é {lead.email}"),
                ("outbound", "Perfeito! Envio ainda hoje. 😊"),
            ]
            for j, (direction, content) in enumerate(convos):
                db.add(Message(
                    tenant_id=tenant.id, instance_id=wa.id, lead_id=lead.id,
                    direction=direction, content=content,
                    status="delivered", external_id=str(uuid.uuid4()),
                    created_at=hours_ago(random.randint(1, 200) + j),
                ))
                mc += 1
        await db.flush()
        print(f"  ✅ 1 instância WA + {mc} mensagens")

        # ── 8. Automations ────────────────────────────────────────────
        for name, trigger, cond, actions in [
            ("Follow-up leads parados 3 dias", "lead_idle",
             {"idle_days": 3}, {"type": "create_task", "title": "Follow-up lead parado"}),
            ("Boas-vindas novo lead", "lead_created",
             {}, {"type": "send_whatsapp", "template": "welcome"}),
            ("Alerta negociação > 7 dias", "lead_idle",
             {"idle_days": 7, "stage": "em_negociacao"}, {"type": "create_task", "title": "Negociação estagnada"}),
        ]:
            db.add(AutomationRule(
                tenant_id=tenant.id, name=name, trigger=trigger,
                conditions=cond, actions=actions, is_active=True,
            ))
        await db.flush()
        print(f"  ✅ 3 automações")

        # ── 9. Documents ──────────────────────────────────────────────
        for fname, ctype, size in [
            ("tabela_precos_unimed_2026.pdf", "application/pdf", 245000),
            ("comparativo_operadoras.xlsx", "application/vnd.ms-excel", 128000),
            ("guia_vendas_planos_saude.pdf", "application/pdf", 1500000),
            ("modelo_contrato_pme.docx", "application/msword", 85000),
        ]:
            db.add(Document(
                tenant_id=tenant.id, filename=str(uuid.uuid4()),
                original_name=fname, s3_key=f"tenants/{tenant.id}/documents/{fname}",
                content_type=ctype, file_size=size,
                embedding_status=random.choice(["done", "done", "pending"]),
                uploaded_by=admin_user.id,
                created_at=days_ago(random.randint(1, 30)),
            ))
        await db.flush()
        print(f"  ✅ 4 documentos")

        # ── 10. Agent Logs ────────────────────────────────────────────
        for query, response in [
            ("Quantos leads novos temos?", "Vocês têm 4 novos leads. Recomendo priorizar contato em 24h."),
            ("Quais leads estão parados?", "3 leads sem interação há mais de 5 dias."),
            ("Resuma conversas do WhatsApp", "12 mensagens com 4 leads hoje. Maria Silva pediu proposta."),
        ]:
            db.add(AgentLog(
                tenant_id=tenant.id, user_id=admin_user.id, action="query",
                input_data={"message": query}, output_data={"response": response},
                status="success", execution_time_ms=random.randint(800, 3000),
                created_at=days_ago(random.randint(0, 5)),
            ))
        await db.flush()
        print(f"  ✅ 3 logs do agente")

        await db.commit()

        print("\n" + "═" * 50)
        print("✅ DEMO DATA COMPLETO!")
        print("═" * 50)
        print(f"  20 leads | {ic} interações | {nc} notas | {tc} tarefas")
        print(f"  3 campanhas | 8 eventos | {mc} msgs WA | 3 automações | 4 docs")
        print(f"\n  Emails: admin@corven.com.br | gestor@corven.com.br | corretor@corven.com.br")


if __name__ == "__main__":
    asyncio.run(seed_demo())
