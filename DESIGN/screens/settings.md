# Settings

## Telas necessárias
1. **Perfil do usuário**
2. **Dados da empresa (tenant)**
3. **Status de integrações**

## Componentes necessários
- Form de perfil (nome, telefone, avatar)
- Form da empresa (nome, logo, settings)
- Painel de integrações com status por provedor

## Dados necessários por tela
### 1) Perfil do usuário
- **API:** `GET /api/v1/settings/profile`
- **API update:** `PATCH /api/v1/settings/profile`
- **Payload update:** `name?`, `phone?`, `avatar_url?`

### 2) Dados da empresa
- **API:** `GET /api/v1/settings/company`
- **API update:** `PATCH /api/v1/settings/company`
- **Payload update:** `name?`, `logo_url?`, `settings?`

### 3) Integrações
- **API:** `GET /api/v1/settings/integrations`
- **Dados:** `whatsapp_evolution`, `whatsapp_meta`, `openai`, `s3_storage`
