import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Notas Lead"
      description="POST /api/v1/leads/{lead_id}/notes"
      queryKey={['leads-[leadId]-notes']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
