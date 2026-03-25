# Mapeamento de Funcionalidades e Fluxos por Módulo

Baseado nos arquivos de `DESIGN/api-mapping`, este documento consolida as funcionalidades do sistema e organiza em módulos de produto.

## 1) Auth

**Funcionalidades**
- Login passwordless com OTP por e-mail.
- Emissão e renovação de tokens JWT.
- Leitura do perfil do usuário autenticado.

**Ações do usuário (fluxos principais)**
1. Solicitar OTP (`/auth/request-otp`).
2. Informar código OTP para autenticar (`/auth/verify-otp`).
3. Renovar sessão com refresh token (`/auth/refresh`).
4. Consultar dados do próprio usuário (`/auth/me`).

## 2) Tenants

**Funcionalidades**
- Gestão global de empresas (multi-tenant), restrita a superadmin.

**Ações do usuário**
1. Listar tenants.
2. Criar tenant.
3. Editar tenant (plano, ativação, settings, logo, slug).

## 3) Users

**Funcionalidades**
- Gestão de usuários com RBAC e escopo por tenant.

**Ações do usuário**
1. Listar usuários.
2. Criar usuário.
3. Consultar usuário por ID.
4. Atualizar dados/perfil/role/ativação/permissões.

## 4) Leads

**Funcionalidades**
- CRM de pipeline de leads com estágio, notas, interações e tarefas.

**Ações do usuário**
1. Listar leads com filtros.
2. Criar lead.
3. Consultar lead por ID.
4. Atualizar dados do lead.
5. Alterar estágio do lead.
6. Listar interações do lead.
7. Adicionar nota ao lead.
8. Criar tarefa de follow-up para lead.

## 5) Dashboard

**Funcionalidades**
- Métricas operacionais por perfil (admin e usuário).

**Ações do usuário**
1. Consultar dashboard administrativo (`/dashboard/admin`).
2. Consultar dashboard de usuário (`/dashboard/user`).

## 6) Campaigns

**Funcionalidades**
- Gestão de campanhas e indicadores de performance.

**Ações do usuário**
1. Listar campanhas.
2. Criar campanha.
3. Consultar campanha por ID.
4. Atualizar campanha (incluindo status).
5. Consultar métricas da campanha.

## 7) WhatsApp

**Funcionalidades**
- Gestão de instâncias WhatsApp por provider.
- Envio e consulta de mensagens.
- Recebimento de webhooks públicos (Evolution/Meta).

**Ações do usuário**
1. Criar instância.
2. Listar instâncias.
3. Consultar status de instância.
4. Enviar mensagem.
5. Listar mensagens.
6. Listar mensagens por lead.
7. (Sistema/provider) enviar webhook para processamento inbound.

## 8) Documents

**Funcionalidades**
- Upload/listagem/remoção de documentos em storage (S3/MinIO).

**Ações do usuário**
1. Upload de documento.
2. Listar documentos.
3. Excluir documento.

## 9) Calendar

**Funcionalidades**
- Agenda de eventos com lembretes e vínculo opcional com lead.

**Ações do usuário**
1. Listar eventos.
2. Listar próximos eventos.
3. Criar evento.
4. Editar evento.
5. Excluir evento.

## 10) Agent

**Funcionalidades**
- Consulta a agente de IA com logging por tenant/usuário.

**Ações do usuário**
1. Enviar consulta ao agente.
2. Consultar logs do agente.

## 11) Automations

**Funcionalidades**
- CRUD de regras de automação por trigger/condição/ação.

**Ações do usuário**
1. Listar regras.
2. Criar regra.
3. Consultar regra por ID.
4. Atualizar regra.
5. Excluir regra.

## 12) Settings

**Funcionalidades**
- Gestão de perfil de usuário, dados da empresa e status de integrações.

**Ações do usuário**
1. Consultar perfil.
2. Atualizar perfil.
3. Consultar dados da empresa.
4. Atualizar dados da empresa.
5. Consultar status de integrações.

## 13) Health

**Funcionalidades**
- Health check público do serviço.

**Ações do usuário/sistema**
1. Consultar `/health` para validar disponibilidade.

---

## Observação
Os estados e erros possíveis por módulo foram detalhados em:
- `DESIGN/states/product-modules-states-errors.md`
