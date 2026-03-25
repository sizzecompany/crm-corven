import { ModulePage } from '@/components/module-page';
import { whatsappService } from '@/services/whatsapp.service';

export default function Page() {
  return (
    <ModulePage
      title="Mensagens por Lead"
      description="GET /api/v1/whatsapp/messages/{lead_id}"
      queryKey={['whatsapp-lead-[leadId]']}
      queryFn={() => whatsappService.messages()}
    />
  );
}
