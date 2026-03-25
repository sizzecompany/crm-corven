import { ModulePage } from '@/components/module-page';
import { tenantsService } from '@/services/tenants.service';

export default function Page() {
  return (
    <ModulePage
      title="Novo Tenant"
      description="POST /api/v1/tenants"
      queryKey={['tenants-new']}
      queryFn={() => tenantsService.list()}
    />
  );
}
