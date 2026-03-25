# Módulo: users

Base path efetivo: `/api/v1/users`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/` | GET | Query: `skip`, `limit` | `UserOut[]` | JWT obrigatório | Sim (admin/user veem apenas próprio tenant; superadmin vê todos) |
| `/` | POST | `UserCreate { email, name, phone?, role, tenant_id? }` | `UserOut` | `superadmin` ou `admin` | Sim (admin cria no próprio tenant; superadmin pode informar tenant_id) |
| `/{user_id}` | GET | Path: `user_id` | `UserOut` | JWT obrigatório | Sim (não-superadmin só acessa usuários do próprio tenant) |
| `/{user_id}` | PATCH | `UserUpdate { name?, phone?, role?, is_active?, custom_permissions?, avatar_url? }` | `UserOut` | `superadmin` ou `admin` | Sim (não-superadmin só altera usuários do próprio tenant) |
