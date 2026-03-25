# API Mapping — Visão Geral do Backend

## 1) Módulos do sistema

Módulos HTTP registrados em `app/main.py`:

1. `auth`
2. `tenants`
3. `users`
4. `leads`
5. `dashboard`
6. `campaigns`
7. `whatsapp`
8. `documents`
9. `calendar`
10. `agent`
11. `automations`
12. `settings`
13. `health` (rota raiz de health check fora de `app/modules`)

Prefixo global da API: `/api/v1`.

## 2) Modelos de banco (SQLAlchemy)

1. `Tenant` (`tenants`)
2. `User` (`users`)
3. `OTPCode` (`otp_codes`)
4. `Lead` (`leads`)
5. `LeadInteraction` (`lead_interactions`)
6. `LeadNote` (`lead_notes`)
7. `Task` (`tasks`)
8. `Campaign` (`campaigns`)
9. `WhatsAppInstance` (`whatsapp_instances`)
10. `Message` (`messages`)
11. `Document` (`documents`)
12. `Event` (`events`)
13. `AutomationRule` (`automation_rules`)
14. `AgentLog` (`agent_logs`)

## 3) Regras globais de autorização

- Autenticação padrão: Bearer JWT via `CurrentUser`.
- Controle de papel (RBAC): `superadmin`, `admin`, `user`.
- Em rotas públicas (`/health`, `/auth/request-otp`, `/auth/verify-otp`, `/auth/refresh`, `/whatsapp/webhook/*`, docs), não há exigência de token.
- Isolamento multi-tenant: consultas quase sempre filtram por `current_user.tenant_id`; exceção principal é módulo `tenants` (escopo global de superadmin).

## 4) Integrações externas mapeadas

1. **PostgreSQL** (persistência principal via SQLAlchemy/asyncpg).
2. **Redis** (broker/result backend Celery, rate limiting indireto via infraestrutura).
3. **Celery** (workers assíncronos para automações).
4. **OpenAI API** (módulo `agent`, `AsyncOpenAI`).
5. **WhatsApp Evolution API** (provider não oficial via HTTPX).
6. **Meta WhatsApp Cloud API** (Graph API oficial via HTTPX).
7. **S3/MinIO** via `boto3` (upload e remoção de documentos).
8. **Sentry/GlitchTip** (`sentry_sdk` em app e worker).
9. **SMTP** (configurado para OTP; envio ainda marcado como TODO no serviço atual).
