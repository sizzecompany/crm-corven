# Auth

## Telas necessárias
1. **Login (solicitar OTP)**
2. **Verificação OTP**
3. **Sessão/Perfil rápido (dados de `/auth/me`)**

## Componentes necessários
- Formulário de e-mail
- Campo OTP (6 dígitos) com contador de reenvio
- Botão de reenviar código
- Feedback de loading/sucesso/erro
- Card de sessão atual (nome, e-mail, role, tenant)

## Dados necessários por tela
### 1) Login (solicitar OTP)
- **Entrada do usuário:** `email`
- **API:** `POST /api/v1/auth/request-otp`
- **Resposta usada na UI:** `message` (e `otp_code_dev_only` em ambiente dev)

### 2) Verificação OTP
- **Entrada do usuário:** `email`, `code`
- **API:** `POST /api/v1/auth/verify-otp`
- **Resposta usada na UI:** `access_token`, `refresh_token`, `token_type`
- **Apoio de sessão:** `POST /api/v1/auth/refresh`

### 3) Sessão/Perfil rápido
- **API:** `GET /api/v1/auth/me`
- **Resposta usada na UI:** `id`, `email`, `name`, `role`, `tenant_id`, `phone`, `avatar_url`
