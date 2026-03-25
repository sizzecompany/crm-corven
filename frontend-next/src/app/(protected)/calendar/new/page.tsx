import { ModulePage } from '@/components/module-page';
import { calendarService } from '@/services/calendar.service';

export default function Page() {
  return (
    <ModulePage
      title="Novo Evento"
      description="POST /api/v1/calendar"
      queryKey={['calendar-new']}
      queryFn={() => calendarService.list()}
    />
  );
}
