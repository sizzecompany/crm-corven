# CRM Corven — SaaS CRM for Health Insurance Brokers

Backend completo em **FastAPI** para plataforma SaaS multi-tenant focada em CRM e automação para corretores de planos de saúde.

## 🚀 Quick Start

### 1. Infraestrutura (Docker)
```bash
docker-compose up -d
```

### 2. Instalar dependências
```bash
pip install -e ".[dev]"
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com suas configurações
```

### 4. Rodar migrations
```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 5. Seed (dados iniciais)
```bash
python -m app.seed
```

### 6. Iniciar servidor
```bash
uvicorn app.main:app --reload --port 8000
```

### 7. Acessar documentação da API
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📁 Estrutura

```
app/
├── main.py                    # FastAPI app factory
├── config.py                  # Settings (pydantic-settings)
├── database.py                # SQLAlchemy async engine
├── dependencies.py            # DI (auth, tenant, permissions)
├── seed.py                    # Database seed script
├── core/
│   ├── security.py            # JWT + OTP
│   ├── permissions.py         # RBAC granular
│   └── exceptions.py          # Custom exceptions
├── middleware/
│   └── tenant.py              # Multi-tenant middleware
├── models/                    # SQLAlchemy ORM models
│   ├── tenant.py
│   ├── user.py
│   ├── lead.py
│   ├── task.py
│   ├── campaign.py
│   ├── whatsapp.py
│   ├── document.py
│   ├── event.py
│   ├── automation.py
│   └── agent_log.py
├── modules/                   # Domain modules
│   ├── auth/                  # OTP login + JWT
│   ├── tenants/               # Tenant CRUD (superadmin)
│   ├── users/                 # User management
│   ├── leads/                 # CRM Kanban pipeline
│   ├── dashboard/             # Metrics + charts
│   ├── campaigns/             # Campaign management
│   ├── whatsapp/              # WhatsApp integration
│   │   └── providers/         # Evolution + Meta providers
│   ├── documents/             # RAG document upload
│   ├── calendar/              # Agenda + events
│   ├── agent/                 # AI Agent (OpenAI)
│   ├── automations/           # Rule engine
│   └── settings/              # Profile + company + integrations
└── workers/
    └── automation_worker.py   # Celery background tasks
```

## 🔑 Usuários de Teste (após seed)

| Role | Email | Descrição |
|------|-------|-----------|
| SUPERADMIN | admin@corven.com.br | Acesso total |
| ADMIN | gestor@corven.com.br | Gestor da empresa |
| USER | corretor@corven.com.br | Corretor |

## 🔐 Autenticação

Login via OTP (código por email):
1. `POST /api/v1/auth/request-otp` → recebe código
2. `POST /api/v1/auth/verify-otp` → recebe JWT tokens
3. Use o `access_token` no header: `Authorization: Bearer <token>`
