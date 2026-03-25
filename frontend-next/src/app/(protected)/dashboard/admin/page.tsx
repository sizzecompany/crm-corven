import { ModulePage } from '@/components/module-page';
import { dashboardService } from '@/services/dashboard.service';

export default function Page() {
  return (
    <ModulePage
      title="Dashboard Admin"
      description="GET /api/v1/dashboard/admin"
      queryKey={['dashboard-admin']}
      queryFn={() => dashboardService.admin()}
    />
  );
}
