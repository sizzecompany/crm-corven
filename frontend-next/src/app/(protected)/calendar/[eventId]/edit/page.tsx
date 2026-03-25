import { ModulePage } from '@/components/module-page';
import { calendarService } from '@/services/calendar.service';

export default function Page() {
  return (
    <ModulePage
      title="Editar Evento"
      description="PATCH/DELETE /api/v1/calendar/{event_id}"
      queryKey={['calendar-[eventId]-edit']}
      queryFn={() => calendarService.list()}
    />
  );
}
