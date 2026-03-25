import { apiClient } from './api-client';
export const calendarService = {
  list: () => apiClient.get('/api/v1/calendar'),
  upcoming: () => apiClient.get('/api/v1/calendar/upcoming'),
  create: (payload: unknown) => apiClient.post('/api/v1/calendar', payload),
  update: (id: string, payload: unknown) => apiClient.patch(`/api/v1/calendar/${id}`, payload),
  remove: (id: string) => apiClient.delete(`/api/v1/calendar/${id}`),
};
