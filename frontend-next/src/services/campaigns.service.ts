import { apiClient } from './api-client';
export const campaignsService = {
  list: (skip = 0, limit = 20) => apiClient.get('/api/v1/campaigns', { params: { skip, limit } }),
  create: (payload: unknown) => apiClient.post('/api/v1/campaigns', payload),
  getById: (id: string) => apiClient.get(`/api/v1/campaigns/${id}`),
  update: (id: string, payload: unknown) => apiClient.patch(`/api/v1/campaigns/${id}`, payload),
  metrics: (id: string) => apiClient.get(`/api/v1/campaigns/${id}/metrics`),
};
