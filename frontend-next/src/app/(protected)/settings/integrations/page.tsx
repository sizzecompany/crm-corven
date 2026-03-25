import { ModulePage } from '@/components/module-page';
import { settingsService } from '@/services/settings.service';

export default function Page() {
  return (
    <ModulePage
      title="Status Integrações"
      description="GET /api/v1/settings/integrations"
      queryKey={['settings-integrations']}
      queryFn={() => settingsService.integrations()}
    />
  );
}
