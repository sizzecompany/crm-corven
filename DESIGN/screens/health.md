# Health

## Telas necessárias
1. **Status do sistema (health check)**

## Componentes necessários
- Indicador visual de disponibilidade (healthy/down)
- Timestamp da última checagem
- Botão de revalidar

## Dados necessários por tela
### 1) Status do sistema
- **API:** `GET /health`
- **Dados:** `status`, `service`
