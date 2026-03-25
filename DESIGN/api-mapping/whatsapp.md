# Módulo: whatsapp

Base path efetivo: `/api/v1/whatsapp`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/instances` | POST | `InstanceCreate { provider, instance_name, phone_number?, config }` | `InstanceOut` | `superadmin` ou `admin` | Sim |
| `/instances` | GET | Query opcional padrão | `InstanceOut[]` | JWT obrigatório | Sim |
| `/instances/{instance_id}/status` | GET | Path: `instance_id` | `{ instance_id, status }` | JWT obrigatório | Sim |
| `/send` | POST | `SendMessageRequest { instance_id, to, content, media_url?, lead_id? }` | `MessageOut` | JWT obrigatório | Sim |
| `/webhook/{provider}` | POST | Payload JSON do provider (Evolution/Meta) | `{ status, message_id? }` | Pública | Não no auth; resolve tenant via instância recebida |
| `/messages` | GET | Query: `skip`, `limit` | `MessageWithLeadOut[]` | JWT obrigatório | Sim |
| `/messages/{lead_id}` | GET | Path: `lead_id`; Query `skip`, `limit` | `MessageOut[]` | JWT obrigatório | Sim |
