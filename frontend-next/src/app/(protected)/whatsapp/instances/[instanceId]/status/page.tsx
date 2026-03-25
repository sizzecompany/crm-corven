import { ModulePage } from '@/components/module-page';
import { whatsappService } from '@/services/whatsapp.service';

export default function Page() {
  return (
    <ModulePage
      title="Status Instância"
      description="GET /api/v1/whatsapp/instances/{instance_id}/status"
      queryKey={['whatsapp-instances-[instanceId]-status']}
      queryFn={() => whatsappService.listInstances()}
    />
  );
}
