import { ModulePage } from '@/components/module-page';
import { automationsService } from '@/services/automations.service';

export default function Page() {
  return (
    <ModulePage
      title="Automations"
      description="GET /api/v1/automations"
      queryKey={['automations']}
      queryFn={() => automationsService.list()}
    />
  );
}
