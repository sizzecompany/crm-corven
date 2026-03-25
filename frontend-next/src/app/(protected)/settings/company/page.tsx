import { ModulePage } from '@/components/module-page';
import { settingsService } from '@/services/settings.service';

export default function Page() {
  return (
    <ModulePage
      title="Dados Empresa"
      description="GET/PATCH /api/v1/settings/company"
      queryKey={['settings-company']}
      queryFn={() => settingsService.company()}
    />
  );
}
