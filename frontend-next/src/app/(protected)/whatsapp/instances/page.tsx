import { ModulePage } from '@/components/module-page';
import { whatsappService } from '@/services/whatsapp.service';

export default function Page() {
  return (
    <ModulePage
      title="Instâncias WhatsApp"
      description="GET /api/v1/whatsapp/instances"
      queryKey={['whatsapp-instances']}
      queryFn={() => whatsappService.listInstances()}
    />
  );
}
