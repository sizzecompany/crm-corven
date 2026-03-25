# frontend-next

Frontend Next.js (App Router) para o CRM Corven, implementado com TypeScript, Tailwind, shadcn/ui, React Query e Zustand.

## Observação importante de design
Durante a leitura foi identificado que `DESIGN/DESIGN.md` não existe no repositório. Como ele foi definido como fonte de verdade para branding/UI, a base visual usada aqui foi a mínima possível para viabilizar execução.

## Stack
- Next.js 15 + App Router
- TypeScript
- Tailwind CSS
- shadcn/ui (estrutura base com `components.json`)
- React Query
- Zustand

## Estrutura
```
/src
  /modules
  /components
  /services
  /hooks
  /store
  /types
```

## Autenticação
- JWT com armazenamento local
- Middleware para rotas protegidas
- Interceptor de API para redirecionamento em `401`

## Telas implementadas (baseadas em `DESIGN/screens`)
- Auth: `/auth/login`, `/auth/verify`, `/auth/session`
- Health: `/health`
- Dashboard: `/dashboard/admin`, `/dashboard/user`
- Tenants: `/tenants`, `/tenants/new`, `/tenants/[tenantId]/edit`
- Users: `/users`, `/users/new`, `/users/[userId]`, `/users/[userId]/edit`
- Leads: `/leads`, `/leads/new`, `/leads/[leadId]`, `/leads/[leadId]/interactions`, `/leads/[leadId]/notes`, `/leads/[leadId]/tasks`
- Campaigns: `/campaigns`, `/campaigns/new`, `/campaigns/[campaignId]`, `/campaigns/[campaignId]/metrics`
- WhatsApp: `/whatsapp/instances`, `/whatsapp/instances/new`, `/whatsapp/instances/[instanceId]/status`, `/whatsapp/messaging`, `/whatsapp/lead/[leadId]`
- Documents: `/documents`, `/documents/upload`
- Calendar: `/calendar`, `/calendar/upcoming`, `/calendar/new`, `/calendar/[eventId]/edit`
- Agent: `/agent`, `/agent/logs`
- Automations: `/automations`, `/automations/new`, `/automations/[ruleId]`, `/automations/[ruleId]/edit`
- Settings: `/settings/profile`, `/settings/company`, `/settings/integrations`

## Rodando localmente
```bash
cd frontend-next
npm install
npm run dev
```

## Variáveis de ambiente
Copie `.env.example` para `.env.local` e ajuste:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
