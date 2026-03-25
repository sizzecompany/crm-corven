import { ModulePage } from '@/components/module-page';
import { dashboardService } from '@/services/dashboard.service';

export default function Page() {
  return (
    <ModulePage
      title="Dashboard Usuário"
      description="GET /api/v1/dashboard/user"
      queryKey={['dashboard-user']}
      queryFn={() => dashboardService.user()}
    />
  );
}
