import { ModulePage } from '@/components/module-page';
import { campaignsService } from '@/services/campaigns.service';

export default function Page() {
  return (
    <ModulePage
      title="Detalhe Campanha"
      description="GET/PATCH /api/v1/campaigns/{campaign_id}"
      queryKey={['campaigns-[campaignId]']}
      queryFn={() => campaignsService.list()}
    />
  );
}
