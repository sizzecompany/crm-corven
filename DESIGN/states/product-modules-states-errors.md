# Estados e Erros por Módulo de Produto

Baseado no `api-mapping`, cada módulo abaixo contém: ações do usuário, estados possíveis e erros possíveis.

## 1) Auth

**Ações do usuário**
- Solicitar OTP.
- Verificar OTP.
- Renovar token.
- Consultar usuário autenticado.

**Estados possíveis**
- Não autenticado.
- OTP solicitado (pendente de validação).
- OTP validado.
- Sessão autenticada (access token válido).
- Sessão expirada (necessita refresh).

**Erros possíveis**
- `400` e-mail inválido ou payload inválido.
- `401` OTP inválido/expirado ou refresh inválido.
- `404` usuário não encontrado para e-mail informado.
- `429` limite de requisições de OTP excedido.
- `500` erro interno ao gerar/validar tokens.

## 2) Tenants

**Ações do usuário**
- Listar tenants.
- Criar tenant.
- Atualizar tenant.

**Estados possíveis**
- Tenant ativo.
- Tenant inativo.
- Tenant em plano definido (ex.: basic/pro).
- Tenant com settings atualizados.

**Erros possíveis**
- `401` não autenticado.
- `403` usuário sem papel `superadmin`.
- `404` tenant não encontrado.
- `409` slug de tenant já existente.
- `422` payload inválido.

## 3) Users

**Ações do usuário**
- Listar usuários.
- Criar usuário.
- Obter usuário por ID.
- Atualizar usuário.

**Estados possíveis**
- Usuário ativo.
- Usuário inativo.
- Papéis: `superadmin`, `admin`, `user`.
- Usuário dentro/fora do escopo do tenant do solicitante.

**Erros possíveis**
- `401` não autenticado.
- `403` sem permissão de papel/tenant.
- `404` usuário não encontrado.
- `409` e-mail já cadastrado.
- `422` validação de dados falhou.

## 4) Leads

**Ações do usuário**
- Listar/criar/consultar/editar lead.
- Alterar estágio.
- Consultar interações.
- Criar nota.
- Criar tarefa.

**Estados possíveis**
- Lead em estágio de pipeline (novo, contato, qualificado, ganho, perdido etc.).
- Lead atribuído ou não atribuído.
- Lead com score definido/indefinido.
- Lead com notas/interações/tarefas vinculadas.

**Erros possíveis**
- `401` não autenticado.
- `403` sem acesso ao lead do tenant ou papel restrito.
- `404` lead/campanha/usuário relacionado não encontrado.
- `422` estágio inválido ou payload inválido.
- `500` erro ao persistir relacionamentos (nota/tarefa/interação).

## 5) Dashboard

**Ações do usuário**
- Consultar dashboard admin.
- Consultar dashboard de usuário.

**Estados possíveis**
- Dashboard admin disponível (para `admin/superadmin`).
- Dashboard user disponível.
- Métricas vazias (sem dados no período).

**Erros possíveis**
- `401` não autenticado.
- `403` papel `user` tentando acessar dashboard admin.
- `500` erro de agregação/consulta de métricas.

## 6) Campaigns

**Ações do usuário**
- Listar/criar/consultar/editar campanha.
- Consultar métricas da campanha.

**Estados possíveis**
- Campanha ativa/pausada/finalizada (conforme status).
- Campanha com orçamento e período definidos/abertos.
- Campanha com métricas calculadas.

**Erros possíveis**
- `401` não autenticado.
- `403` sem permissão para criar/editar.
- `404` campanha não encontrada.
- `422` payload inválido (datas/orçamento/status).
- `500` erro ao calcular métricas.

## 7) WhatsApp

**Ações do usuário**
- Criar/listar instâncias.
- Consultar status da instância.
- Enviar mensagem.
- Listar mensagens gerais e por lead.
- Receber/processar webhook.

**Estados possíveis**
- Instância criada.
- Instância conectada/desconectada/em pareamento.
- Mensagem outbound pendente/enviada/falha.
- Mensagem inbound recebida/processada.

**Erros possíveis**
- `401` não autenticado (exceto webhook público).
- `403` sem permissão de papel para criar instância.
- `404` instância/lead/mensagem não encontrado.
- `422` payload inválido de envio/webhook.
- `502` falha no provider externo (Meta/Evolution).

## 8) Documents

**Ações do usuário**
- Upload de documento.
- Listagem de documentos.
- Exclusão de documento.

**Estados possíveis**
- Documento em upload.
- Documento armazenado e indexado no tenant.
- Documento removido.

**Erros possíveis**
- `401` não autenticado.
- `403` sem acesso ao documento do tenant.
- `404` documento não encontrado.
- `413` arquivo excede limite permitido.
- `502` falha no storage S3/MinIO.

## 9) Calendar

**Ações do usuário**
- Listar eventos.
- Listar próximos eventos.
- Criar/editar/excluir evento.

**Estados possíveis**
- Evento criado.
- Evento atualizado.
- Evento com/sem vínculo de lead.
- Evento all-day vs com horário.
- Evento com lembrete configurado.

**Erros possíveis**
- `401` não autenticado.
- `403` sem acesso ao evento de outro usuário/tenant.
- `404` evento não encontrado.
- `422` datas inválidas (início/fim) ou payload inválido.

## 10) Agent

**Ações do usuário**
- Enviar pergunta ao agente.
- Listar logs do agente.

**Estados possíveis**
- Consulta recebida.
- Resposta gerada.
- Log gravado.
- Sugestões/ações retornadas.

**Erros possíveis**
- `401` não autenticado.
- `403` sem acesso aos logs (escopo de papel).
- `422` payload da consulta inválido.
- `429` limite de consumo da IA atingido.
- `502` indisponibilidade da API OpenAI.

## 11) Automations

**Ações do usuário**
- Listar/criar/consultar/editar/excluir regra.

**Estados possíveis**
- Regra ativa.
- Regra inativa.
- Regra com trigger/condições/ações válidos.
- Regra em execução (assíncrona via worker).

**Erros possíveis**
- `401` não autenticado.
- `403` sem permissão (`admin/superadmin` apenas).
- `404` regra não encontrada.
- `422` definição inválida de trigger/condições/ações.
- `500` falha no worker/execução da automação.

## 12) Settings

**Ações do usuário**
- Consultar/editar perfil.
- Consultar/editar dados da empresa.
- Consultar status das integrações.

**Estados possíveis**
- Perfil atualizado/desatualizado.
- Dados da empresa atualizados/desatualizados.
- Integrações ativas/inativas por provider.

**Erros possíveis**
- `401` não autenticado.
- `403` sem permissão para editar company.
- `404` tenant/perfil não encontrado.
- `422` payload inválido (telefone, avatar, settings etc.).

## 13) Health

**Ações do usuário/sistema**
- Consultar endpoint de health.

**Estados possíveis**
- Serviço saudável (`healthy`).
- Serviço degradado/indisponível (inferido fora do endpoint).

**Erros possíveis**
- `503` indisponibilidade temporária do serviço.
- `500` falha interna no processo de health check.
