import { ModulePage } from '@/components/module-page';
import { tenantsService } from '@/services/tenants.service';

export default function Page() {
  return (
    <ModulePage
      title="Editar Tenant"
      description="PATCH /api/v1/tenants/{tenant_id}"
      queryKey={['tenants-[tenantId]-edit']}
      queryFn={() => tenantsService.list()}
    />
  );
}
