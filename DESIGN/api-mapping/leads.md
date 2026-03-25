# Módulo: leads

Base path efetivo: `/api/v1/leads`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Query: `stage?`, `source?`, `assigned_to?`, `skip`, `limit` | `LeadOut[]` | JWT obrigatório | Sim (sempre filtrado por tenant; papel `user` só vê seus leads atribuídos) |
| `/` | POST | `LeadCreate { name, email?, phone?, source?, campaign_id?, assigned_to?, metadata_extra? }` | `LeadOut` | JWT obrigatório | Sim |
| `/{lead_id}` | GET | Path: `lead_id` | `LeadOut` | JWT obrigatório | Sim |
| `/{lead_id}` | PATCH | `LeadUpdate { name?, email?, phone?, source?, assigned_to?, metadata_extra?, score? }` | `LeadOut` | JWT obrigatório | Sim |
| `/{lead_id}/stage` | PATCH | `LeadStageUpdate { stage }` | `LeadOut` | JWT obrigatório | Sim |
| `/{lead_id}/interactions` | GET | Path: `lead_id` | `InteractionOut[]` | JWT obrigatório | Sim |
| `/{lead_id}/notes` | POST | `NoteCreate { content }` | `NoteOut` | JWT obrigatório | Sim |
| `/{lead_id}/tasks` | POST | `TaskCreate { title, description?, due_date?, assigned_to?, is_follow_up }` | `TaskOut` | JWT obrigatório | Sim |
