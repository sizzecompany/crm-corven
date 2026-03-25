import { ModulePage } from '@/components/module-page';
import { tenantsService } from '@/services/tenants.service';

export default function Page() {
  return (
    <ModulePage
      title="Tenants"
      description="GET /api/v1/tenants?skip&limit"
      queryKey={['tenants']}
      queryFn={() => tenantsService.list()}
    />
  );
}
