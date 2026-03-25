# Users

## Telas necessárias
1. **Lista de usuários**
2. **Cadastro de usuário**
3. **Detalhe de usuário**
4. **Edição de usuário/permissões**

## Componentes necessários
- Tabela de usuários com paginação
- Badge de role/status
- Drawer/modal de criação
- Formulário de usuário (dados básicos + role)
- Editor de permissões customizadas (JSON/chips)

## Dados necessários por tela
### 1) Lista de usuários
- **API:** `GET /api/v1/users?skip&limit`
- **Dados:** `UserOut[]`

### 2) Cadastro de usuário
- **API:** `POST /api/v1/users`
- **Payload:** `email`, `name`, `phone?`, `role`, `tenant_id?`

### 3) Detalhe de usuário
- **API:** `GET /api/v1/users/{user_id}`
- **Dados:** `UserOut`

### 4) Edição de usuário/permissões
- **API:** `PATCH /api/v1/users/{user_id}`
- **Payload:** `name?`, `phone?`, `role?`, `is_active?`, `custom_permissions?`, `avatar_url?`
