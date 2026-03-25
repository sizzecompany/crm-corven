import { ModulePage } from '@/components/module-page';
import { campaignsService } from '@/services/campaigns.service';

export default function Page() {
  return (
    <ModulePage
      title="Nova Campanha"
      description="POST /api/v1/campaigns"
      queryKey={['campaigns-new']}
      queryFn={() => campaignsService.list()}
    />
  );
}
