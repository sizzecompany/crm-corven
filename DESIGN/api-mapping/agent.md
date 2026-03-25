# Módulo: agent

Base path efetivo: `/api/v1/agent`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/query` | POST | `AgentQuery { message, context? }` | `AgentResponse { response, actions_taken[], suggestions[] }` | JWT obrigatório | Sim (contexto e logs do tenant do usuário) |
| `/logs` | GET | Query: `skip`, `limit` | `AgentLogOut[]` | JWT obrigatório | Sim (`user` vê apenas logs próprios; admin/superadmin veem tenant) |
