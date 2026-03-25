# Módulo: campaigns

Base path efetivo: `/api/v1/campaigns`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Query: `skip`, `limit` | `CampaignOut[]` | JWT obrigatório | Sim |
| `/` | POST | `CampaignCreate { name, source?, budget?, start_date?, end_date?, description?, metadata_extra? }` | `CampaignOut` | `superadmin` ou `admin` | Sim |
| `/{campaign_id}` | GET | Path: `campaign_id` | `CampaignOut` | JWT obrigatório | Sim |
| `/{campaign_id}` | PATCH | `CampaignUpdate { name?, source?, budget?, start_date?, end_date?, status?, description?, metadata_extra? }` | `CampaignOut` | `superadmin` ou `admin` | Sim |
| `/{campaign_id}/metrics` | GET | Path: `campaign_id` | `CampaignMetrics { total_leads, conversions, conversion_rate, cost_per_lead... }` | JWT obrigatório | Sim |
