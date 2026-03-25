import { ModulePage } from '@/components/module-page';
import { agentService } from '@/services/agent.service';

export default function Page() {
  return (
    <ModulePage
      title="Logs Agent"
      description="GET /api/v1/agent/logs"
      queryKey={['agent-logs']}
      queryFn={() => agentService.logs()}
    />
  );
}
