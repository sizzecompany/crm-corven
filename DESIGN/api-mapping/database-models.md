# Modelos de Banco (com tabelas)

| Modelo | Tabela | Observação |
|---|---|---|
| `Tenant` | `tenants` | Entidade de tenant/empresa (plano, settings, ativação). |
| `User` | `users` | Usuário autenticável com role e permissões customizadas. |
| `OTPCode` | `otp_codes` | Códigos OTP para login passwordless. |
| `Lead` | `leads` | Lead principal do CRM (pipeline). |
| `LeadInteraction` | `lead_interactions` | Histórico de interações por lead. |
| `LeadNote` | `lead_notes` | Notas textuais do lead. |
| `Task` | `tasks` | Tarefas/follow-ups (vinculáveis a lead). |
| `Campaign` | `campaigns` | Campanhas de aquisição/conversão. |
| `WhatsAppInstance` | `whatsapp_instances` | Instâncias/conexões por provider WhatsApp. |
| `Message` | `messages` | Mensagens inbound/outbound WhatsApp. |
| `Document` | `documents` | Metadados de documentos enviados ao storage/RAG. |
| `Event` | `events` | Agenda/calendário e lembretes. |
| `AutomationRule` | `automation_rules` | Regras de automação por trigger/condições/ações. |
| `AgentLog` | `agent_logs` | Log de execução do módulo de IA. |
