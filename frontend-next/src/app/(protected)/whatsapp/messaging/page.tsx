import { ModulePage } from '@/components/module-page';
import { whatsappService } from '@/services/whatsapp.service';

export default function Page() {
  return (
    <ModulePage
      title="Central de Mensagens"
      description="GET /api/v1/whatsapp/messages + POST /send"
      queryKey={['whatsapp-messaging']}
      queryFn={() => whatsappService.messages()}
    />
  );
}
