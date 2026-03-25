import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Interações Lead"
      description="GET /api/v1/leads/{lead_id}/interactions"
      queryKey={['leads-[leadId]-interactions']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
