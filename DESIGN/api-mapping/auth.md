# Módulo: auth

Base path efetivo: `/api/v1/auth`.

| Endpoint | Método | Payload esperado | Resposta | Autorização | Dependência de tenant |
|---|---|---|---|---|---|
| `/request-otp` | POST | `OTPRequest { email }` | `{ message, otp_code_dev_only? }` | Pública (limitada a 3/min) | Não |
| `/verify-otp` | POST | `OTPVerify { email, code }` | `TokenResponse { access_token, refresh_token, token_type }` | Pública | Não direto (token pode carregar tenant) |
| `/refresh` | POST | `RefreshRequest { refresh_token }` | `TokenResponse` | Pública | Não direto |
| `/me` | GET | Sem payload | `UserProfile { id, email, name, role, tenant_id, phone, avatar_url }` | JWT obrigatório | Sim (vem do usuário autenticado) |
