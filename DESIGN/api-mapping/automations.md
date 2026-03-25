# Módulo: automations

Base path efetivo: `/api/v1/automations`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Sem payload | `AutomationOut[]` | `superadmin` ou `admin` | Sim |
| `/` | POST | `AutomationCreate { name, description?, trigger, conditions, actions, is_active }` | `AutomationOut` | `superadmin` ou `admin` | Sim |
| `/{rule_id}` | GET | Path: `rule_id` | `AutomationOut` | `superadmin` ou `admin` | Sim |
| `/{rule_id}` | PATCH | `AutomationUpdate { name?, description?, trigger?, conditions?, actions?, is_active? }` | `AutomationOut` | `superadmin` ou `admin` | Sim |
| `/{rule_id}` | DELETE | Path: `rule_id` | `204 No Content` | `superadmin` ou `admin` | Sim |
