import { ModulePage } from '@/components/module-page';
import { usersService } from '@/services/users.service';

export default function Page() {
  return (
    <ModulePage
      title="Usuários"
      description="GET /api/v1/users?skip&limit"
      queryKey={['users']}
      queryFn={() => usersService.list()}
    />
  );
}
