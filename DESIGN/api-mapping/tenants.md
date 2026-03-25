# Módulo: tenants

Base path efetivo: `/api/v1/tenants`.

> Escopo administrativo global (não é tenant-scoped para listagem/criação/edição).

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Query: `skip`, `limit` | `TenantOut[]` | `superadmin` | Não |
| `/` | POST | `TenantCreate { name, slug, plan }` | `TenantOut` | `superadmin` | Não |
| `/{tenant_id}` | PATCH | `TenantUpdate { name?, slug?, plan?, is_active?, settings?, logo_url? }` | `TenantOut` | `superadmin` | Não |
