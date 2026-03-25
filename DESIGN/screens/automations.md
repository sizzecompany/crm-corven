# Automations

## Telas necessárias
1. **Lista de regras**
2. **Criação de regra**
3. **Detalhe/Edição de regra**

## Componentes necessários
- Tabela de regras com status (ativo/inativo)
- Builder de trigger/condições/ações
- Editor JSON assistido (opcional)
- Confirmação de exclusão

## Dados necessários por tela
### 1) Lista de regras
- **API:** `GET /api/v1/automations`
- **Dados:** `AutomationOut[]`

### 2) Criação de regra
- **API:** `POST /api/v1/automations`
- **Payload:** `name`, `description?`, `trigger`, `conditions`, `actions`, `is_active`

### 3) Detalhe/Edição
- **API detalhe:** `GET /api/v1/automations/{rule_id}`
- **API edição:** `PATCH /api/v1/automations/{rule_id}`
- **API exclusão:** `DELETE /api/v1/automations/{rule_id}`
