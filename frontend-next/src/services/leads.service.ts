import { apiClient } from './api-client';
export const leadsService = {
  list: (params: Record<string, unknown>) => apiClient.get('/api/v1/leads', { params }),
  create: (payload: unknown) => apiClient.post('/api/v1/leads', payload),
  getById: (id: string) => apiClient.get(`/api/v1/leads/${id}`),
  update: (id: string, payload: unknown) => apiClient.patch(`/api/v1/leads/${id}`, payload),
  updateStage: (id: string, stage: string) => apiClient.patch(`/api/v1/leads/${id}/stage`, { stage }),
  interactions: (id: string) => apiClient.get(`/api/v1/leads/${id}/interactions`),
  addNote: (id: string, content: string) => apiClient.post(`/api/v1/leads/${id}/notes`, { content }),
  addTask: (id: string, payload: unknown) => apiClient.post(`/api/v1/leads/${id}/tasks`, payload),
};
