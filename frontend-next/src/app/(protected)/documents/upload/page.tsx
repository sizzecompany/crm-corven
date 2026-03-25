import { ModulePage } from '@/components/module-page';
import { documentsService } from '@/services/documents.service';

export default function Page() {
  return (
    <ModulePage
      title="Upload Documento"
      description="POST /api/v1/documents/upload"
      queryKey={['documents-upload']}
      queryFn={() => documentsService.list()}
    />
  );
}
