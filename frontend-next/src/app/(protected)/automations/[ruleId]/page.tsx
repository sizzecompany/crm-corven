import { ModulePage } from '@/components/module-page';
import { automationsService } from '@/services/automations.service';

export default function Page() {
  return (
    <ModulePage
      title="Detalhe Regra"
      description="GET /api/v1/automations/{rule_id}"
      queryKey={['automations-[ruleId]']}
      queryFn={() => automationsService.list()}
    />
  );
}
