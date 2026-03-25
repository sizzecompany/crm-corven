# Módulo: dashboard

Base path efetivo: `/api/v1/dashboard`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/admin` | GET | Sem payload | `DashboardMetrics` | JWT obrigatório; bloqueia papel `user` (somente `admin/superadmin`) | Sim |
| `/user` | GET | Sem payload | `UserDashboardMetrics` | JWT obrigatório | Sim |
