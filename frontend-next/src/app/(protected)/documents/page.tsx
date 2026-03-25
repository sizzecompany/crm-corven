import { ModulePage } from '@/components/module-page';
import { documentsService } from '@/services/documents.service';

export default function Page() {
  return (
    <ModulePage
      title="Biblioteca Documentos"
      description="GET /api/v1/documents"
      queryKey={['documents']}
      queryFn={() => documentsService.list()}
    />
  );
}
