import { ModulePage } from '@/components/module-page';
import { campaignsService } from '@/services/campaigns.service';

export default function Page() {
  return (
    <ModulePage
      title="Campanhas"
      description="GET /api/v1/campaigns?skip&limit"
      queryKey={['campaigns']}
      queryFn={() => campaignsService.list()}
    />
  );
}
