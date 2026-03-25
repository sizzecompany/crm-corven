import { ModulePage } from '@/components/module-page';
import { automationsService } from '@/services/automations.service';

export default function Page() {
  return (
    <ModulePage
      title="Editar Regra"
      description="PATCH/DELETE /api/v1/automations/{rule_id}"
      queryKey={['automations-[ruleId]-edit']}
      queryFn={() => automationsService.list()}
    />
  );
}
