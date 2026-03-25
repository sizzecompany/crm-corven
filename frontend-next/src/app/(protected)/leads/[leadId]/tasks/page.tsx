import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Tarefas Lead"
      description="POST /api/v1/leads/{lead_id}/tasks"
      queryKey={['leads-[leadId]-tasks']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
