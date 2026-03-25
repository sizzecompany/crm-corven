# Calendar

## Telas necessárias
1. **Calendário (mês/semana/dia)**
2. **Próximos eventos**
3. **Criação/Edição de evento**

## Componentes necessários
- Grade de calendário
- Lista de próximos eventos
- Modal/form de evento
- Campo de vínculo com lead (opcional)
- Configuração de lembrete

## Dados necessários por tela
### 1) Calendário
- **API:** `GET /api/v1/calendar`
- **Dados:** `EventOut[]`

### 2) Próximos eventos
- **API:** `GET /api/v1/calendar/upcoming`
- **Dados:** `EventOut[]`

### 3) Criação/Edição
- **API criação:** `POST /api/v1/calendar`
- **Payload criação:** `title`, `description?`, `start_datetime`, `end_datetime?`, `all_day`, `location?`, `lead_id?`, `reminder_minutes`
- **API edição:** `PATCH /api/v1/calendar/{event_id}`
- **API exclusão:** `DELETE /api/v1/calendar/{event_id}`
