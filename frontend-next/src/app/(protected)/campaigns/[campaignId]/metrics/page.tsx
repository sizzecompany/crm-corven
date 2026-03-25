import { ModulePage } from '@/components/module-page';
import { campaignsService } from '@/services/campaigns.service';

export default function Page() {
  return (
    <ModulePage
      title="Métricas Campanha"
      description="GET /api/v1/campaigns/{campaign_id}/metrics"
      queryKey={['campaigns-[campaignId]-metrics']}
      queryFn={() => campaignsService.list()}
    />
  );
}
