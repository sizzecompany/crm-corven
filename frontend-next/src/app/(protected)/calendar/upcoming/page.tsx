import { ModulePage } from '@/components/module-page';
import { calendarService } from '@/services/calendar.service';

export default function Page() {
  return (
    <ModulePage
      title="Próximos Eventos"
      description="GET /api/v1/calendar/upcoming"
      queryKey={['calendar-upcoming']}
      queryFn={() => calendarService.upcoming()}
    />
  );
}
