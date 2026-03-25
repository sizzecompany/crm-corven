import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Detalhe 360 Lead"
      description="GET/PATCH /api/v1/leads/{lead_id}"
      queryKey={['leads-[leadId]']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
