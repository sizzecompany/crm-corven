import { ModulePage } from '@/components/module-page';
import { automationsService } from '@/services/automations.service';

export default function Page() {
  return (
    <ModulePage
      title="Nova Regra"
      description="POST /api/v1/automations"
      queryKey={['automations-new']}
      queryFn={() => automationsService.list()}
    />
  );
}
