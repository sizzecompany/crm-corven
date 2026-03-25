# Módulo: settings

Base path efetivo: `/api/v1/settings`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/profile` | GET | Sem payload | `ProfileOut` | JWT obrigatório | Indireta (usuário autenticado) |
| `/profile` | PATCH | `ProfileUpdate { name?, phone?, avatar_url? }` | `ProfileOut` | JWT obrigatório | Indireta |
| `/company` | GET | Sem payload | `CompanyOut` | JWT obrigatório | Sim (busca tenant atual) |
| `/company` | PATCH | `CompanyUpdate { name?, logo_url?, settings? }` | `CompanyOut` | `superadmin` ou `admin` | Sim |
| `/integrations` | GET | Sem payload | `IntegrationStatus { whatsapp_evolution, whatsapp_meta, openai, s3_storage }` | JWT obrigatório | Não estrita (status por configuração global do ambiente) |
