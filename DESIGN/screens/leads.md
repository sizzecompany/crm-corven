# Leads

## Telas necessárias
1. **Lista/Kanban de leads**
2. **Cadastro de lead**
3. **Detalhe 360º do lead**
4. **Interações do lead**
5. **Notas do lead**
6. **Tarefas/follow-up do lead**

## Componentes necessários
- Board Kanban por estágio + tabela alternativa
- Filtros (stage, source, assigned_to)
- Formulário de lead
- Header com score/stage/owner
- Timeline de interações
- Editor de nota
- Formulário rápido de tarefa

## Dados necessários por tela
### 1) Lista/Kanban
- **API:** `GET /api/v1/leads?stage&source&assigned_to&skip&limit`
- **Dados:** `LeadOut[]`

### 2) Cadastro de lead
- **API:** `POST /api/v1/leads`
- **Payload:** `name`, `email?`, `phone?`, `source?`, `campaign_id?`, `assigned_to?`, `metadata_extra?`

### 3) Detalhe 360º
- **API:** `GET /api/v1/leads/{lead_id}`
- **API (mudança estágio):** `PATCH /api/v1/leads/{lead_id}/stage`
- **API (edição):** `PATCH /api/v1/leads/{lead_id}`

### 4) Interações
- **API:** `GET /api/v1/leads/{lead_id}/interactions`
- **Dados:** `InteractionOut[]`

### 5) Notas
- **API:** `POST /api/v1/leads/{lead_id}/notes`
- **Payload:** `content`
- **Dados exibidos:** `NoteOut`

### 6) Tarefas/follow-up
- **API:** `POST /api/v1/leads/{lead_id}/tasks`
- **Payload:** `title`, `description?`, `due_date?`, `assigned_to?`, `is_follow_up`
- **Dados exibidos:** `TaskOut`
