import { ModulePage } from '@/components/module-page';
import { agentService } from '@/services/agent.service';

export default function Page() {
  return (
    <ModulePage
      title="Chat Agent"
      description="POST /api/v1/agent/query"
      queryKey={['agent']}
      queryFn={() => agentService.logs()}
    />
  );
}
