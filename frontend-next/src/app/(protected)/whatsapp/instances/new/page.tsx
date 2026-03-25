import { ModulePage } from '@/components/module-page';
import { whatsappService } from '@/services/whatsapp.service';

export default function Page() {
  return (
    <ModulePage
      title="Cadastro Instância"
      description="POST /api/v1/whatsapp/instances"
      queryKey={['whatsapp-instances-new']}
      queryFn={() => whatsappService.listInstances()}
    />
  );
}
