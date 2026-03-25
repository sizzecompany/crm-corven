# WhatsApp

## Telas necessárias
1. **Lista de instâncias**
2. **Cadastro de instância**
3. **Status da instância**
4. **Central de mensagens (caixa de conversa)**
5. **Mensagens por lead**

## Componentes necessários
- Cards/tabela de instâncias por provider
- Form de configuração da instância
- Indicador de status em tempo real
- Lista de conversas/mensagens
- Composer de mensagem (texto/mídia)

## Dados necessários por tela
### 1) Lista de instâncias
- **API:** `GET /api/v1/whatsapp/instances`
- **Dados:** `InstanceOut[]`

### 2) Cadastro de instância
- **API:** `POST /api/v1/whatsapp/instances`
- **Payload:** `provider`, `instance_name`, `phone_number?`, `config`

### 3) Status da instância
- **API:** `GET /api/v1/whatsapp/instances/{instance_id}/status`
- **Dados:** `instance_id`, `status`

### 4) Central de mensagens
- **API envio:** `POST /api/v1/whatsapp/send`
- **Payload envio:** `instance_id`, `to`, `content`, `media_url?`, `lead_id?`
- **API listagem:** `GET /api/v1/whatsapp/messages?skip&limit`
- **Dados listagem:** `MessageWithLeadOut[]`

### 5) Mensagens por lead
- **API:** `GET /api/v1/whatsapp/messages/{lead_id}?skip&limit`
- **Dados:** `MessageOut[]`
