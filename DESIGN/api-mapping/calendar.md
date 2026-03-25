# Módulo: calendar

Base path efetivo: `/api/v1/calendar`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Sem payload | `EventOut[]` | JWT obrigatório | Sim (filtra por tenant + usuário atual) |
| `/upcoming` | GET | Sem payload | `EventOut[]` | JWT obrigatório | Sim (tenant + usuário atual) |
| `/` | POST | `EventCreate { title, description?, start_datetime, end_datetime?, all_day, location?, lead_id?, reminder_minutes }` | `EventOut` | JWT obrigatório | Sim |
| `/{event_id}` | PATCH | `EventUpdate { title?, description?, start_datetime?, end_datetime?, all_day?, location?, reminder_minutes? }` | `EventOut` | JWT obrigatório | Sim |
| `/{event_id}` | DELETE | Path: `event_id` | `204 No Content` | JWT obrigatório | Sim |
