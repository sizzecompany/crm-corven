import { ModulePage } from '@/components/module-page';
import { leadsService } from '@/services/leads.service';

export default function Page() {
  return (
    <ModulePage
      title="Novo Lead"
      description="POST /api/v1/leads"
      queryKey={['leads-new']}
      queryFn={() => leadsService.list({ skip: 0, limit: 20 })}
    />
  );
}
