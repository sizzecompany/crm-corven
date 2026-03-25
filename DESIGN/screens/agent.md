# Agent

## Telas necessárias
1. **Chat com agente**
2. **Histórico/logs do agente**

## Componentes necessários
- Área de chat (pergunta/resposta)
- Lista de sugestões e ações tomadas
- Filtros de logs (usuário/período)
- Tabela paginada de logs

## Dados necessários por tela
### 1) Chat com agente
- **API:** `POST /api/v1/agent/query`
- **Payload:** `message`, `context?`
- **Resposta:** `response`, `actions_taken[]`, `suggestions[]`

### 2) Histórico/logs
- **API:** `GET /api/v1/agent/logs?skip&limit`
- **Dados:** `AgentLogOut[]`
