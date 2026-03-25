import { apiClient } from './api-client';
export const automationsService = {
  list: () => apiClient.get('/api/v1/automations'),
  create: (payload: unknown) => apiClient.post('/api/v1/automations', payload),
  getById: (id: string) => apiClient.get(`/api/v1/automations/${id}`),
  update: (id: string, payload: unknown) => apiClient.patch(`/api/v1/automations/${id}`, payload),
  remove: (id: string) => apiClient.delete(`/api/v1/automations/${id}`),
};
