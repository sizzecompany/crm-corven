import { ModulePage } from '@/components/module-page';
import { settingsService } from '@/services/settings.service';

export default function Page() {
  return (
    <ModulePage
      title="Perfil Usuário"
      description="GET/PATCH /api/v1/settings/profile"
      queryKey={['settings-profile']}
      queryFn={() => settingsService.profile()}
    />
  );
}
