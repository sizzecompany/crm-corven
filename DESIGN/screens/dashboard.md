# Dashboard

## Telas necessárias
1. **Dashboard admin**
2. **Dashboard usuário**

## Componentes necessários
- Cards de KPI
- Gráficos de tendência/funil
- Lista de atividades/tarefas
- Seletor de período

## Dados necessários por tela
### 1) Dashboard admin
- **API:** `GET /api/v1/dashboard/admin`
- **Dados:** `DashboardMetrics` (visão consolidada do tenant)

### 2) Dashboard usuário
- **API:** `GET /api/v1/dashboard/user`
- **Dados:** `UserDashboardMetrics` (visão individual)
