# Tenants

## Telas necessárias
1. **Lista de tenants**
2. **Cadastro de tenant**
3. **Edição de tenant**

## Componentes necessários
- Tabela paginada de tenants
- Filtros simples (nome/slug/status)
- Formulário de tenant
- Seletor de plano
- Toggle de ativo/inativo
- Upload/URL de logo

## Dados necessários por tela
### 1) Lista de tenants
- **API:** `GET /api/v1/tenants?skip&limit`
- **Dados:** `TenantOut[]` (id, name, slug, plan, is_active, settings, logo_url)

### 2) Cadastro de tenant
- **API:** `POST /api/v1/tenants`
- **Payload:** `name`, `slug`, `plan`
- **Dados auxiliares:** lista de planos permitidos

### 3) Edição de tenant
- **API:** `PATCH /api/v1/tenants/{tenant_id}`
- **Payload:** `name?`, `slug?`, `plan?`, `is_active?`, `settings?`, `logo_url?`
