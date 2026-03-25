import { ModulePage } from '@/components/module-page';
import { usersService } from '@/services/users.service';

export default function Page() {
  return (
    <ModulePage
      title="Editar Usuário"
      description="PATCH /api/v1/users/{user_id}"
      queryKey={['users-[userId]-edit']}
      queryFn={() => usersService.list()}
    />
  );
}
