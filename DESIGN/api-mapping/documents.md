# Módulo: documents

Base path efetivo: `/api/v1/documents`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/upload` | POST | `multipart/form-data` com `file` | `DocumentOut` | JWT obrigatório | Sim |
| `/` | GET | Sem payload | `DocumentOut[]` | JWT obrigatório | Sim |
| `/{doc_id}` | DELETE | Path: `doc_id` | `204 No Content` | JWT obrigatório | Sim |
