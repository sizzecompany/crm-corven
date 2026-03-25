# Campaigns

## Telas necessárias
1. **Lista de campanhas**
2. **Cadastro de campanha**
3. **Detalhe de campanha**
4. **Métricas da campanha**

## Componentes necessários
- Tabela de campanhas
- Badge de status
- Formulário de campanha
- Cards de métricas (CPL, conversão)
- Gráfico de performance por período

## Dados necessários por tela
### 1) Lista de campanhas
- **API:** `GET /api/v1/campaigns?skip&limit`
- **Dados:** `CampaignOut[]`

### 2) Cadastro de campanha
- **API:** `POST /api/v1/campaigns`
- **Payload:** `name`, `source?`, `budget?`, `start_date?`, `end_date?`, `description?`, `metadata_extra?`

### 3) Detalhe/Edição de campanha
- **API:** `GET /api/v1/campaigns/{campaign_id}`
- **API:** `PATCH /api/v1/campaigns/{campaign_id}`

### 4) Métricas da campanha
- **API:** `GET /api/v1/campaigns/{campaign_id}/metrics`
- **Dados:** `total_leads`, `conversions`, `conversion_rate`, `cost_per_lead` e derivados
