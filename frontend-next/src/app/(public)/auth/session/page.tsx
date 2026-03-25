import { ModulePage } from '@/components/module-page';
import { authApi } from '@/services/auth';

export default function SessionPage() {
  return <ModulePage title="Sessão rápida" description="GET /api/v1/auth/me" queryKey={['auth-me']} queryFn={() => authApi.me()} />;
}
