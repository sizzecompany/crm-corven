import { ModulePage } from '@/components/module-page';
import { calendarService } from '@/services/calendar.service';

export default function Page() {
  return (
    <ModulePage
      title="Calendário"
      description="GET /api/v1/calendar"
      queryKey={['calendar']}
      queryFn={() => calendarService.list()}
    />
  );
}
