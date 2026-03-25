import { ModulePage } from '@/components/module-page';
import { usersService } from '@/services/users.service';

export default function Page() {
  return (
    <ModulePage
      title="Novo Usuário"
      description="POST /api/v1/users"
      queryKey={['users-new']}
      queryFn={() => usersService.list()}
    />
  );
}
