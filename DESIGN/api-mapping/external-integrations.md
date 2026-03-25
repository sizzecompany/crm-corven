# Integrações Externas

## Infra e persistência
- **PostgreSQL**: banco principal (`DATABASE_URL`, SQLAlchemy async).
- **Redis**: broker/backend do Celery (`REDIS_URL`).
- **Celery**: execução assíncrona de tarefas de automação.

## Comunicação e canais
- **SMTP**: previsto para envio de OTP por e-mail (no momento com `TODO` no serviço de auth).
- **WhatsApp Evolution API**: criação de instância, status, envio e parsing de webhook.
- **Meta WhatsApp Cloud API (Graph)**: status e envio oficial.

## IA e documentos
- **OpenAI API**: atendimento no módulo `agent` via `AsyncOpenAI`.
- **S3/MinIO (boto3)**: upload/deleção de documentos no bucket configurado.

## Observabilidade
- **Sentry/GlitchTip**: captura de erros no FastAPI e nos workers Celery.
