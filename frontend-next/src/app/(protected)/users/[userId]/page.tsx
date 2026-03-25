import { ModulePage } from '@/components/module-page';
import { usersService } from '@/services/users.service';

export default function Page() {
  return (
    <ModulePage
      title="Detalhe Usuário"
      description="GET /api/v1/users/{user_id}"
      queryKey={['users-[userId]']}
      queryFn={() => usersService.list()}
    />
  );
}
