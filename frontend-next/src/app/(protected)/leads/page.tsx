import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Leads Kanban/Lista"
      description="GET /api/v1/leads?filters"
      queryKey={['leads']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
