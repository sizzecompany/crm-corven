# Módulo: health

Base path efetivo: `/health` (fora de `/api/v1`).

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/health` | GET | Sem payload | `{ "status": "healthy", "service": "crm-corven" }` | Pública | Não |
