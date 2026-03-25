import { apiClient } from './api-client';
export const usersService = {
  list: (skip = 0, limit = 20) => apiClient.get('/api/v1/users', { params: { skip, limit } }),
  create: (payload: unknown) => apiClient.post('/api/v1/users', payload),
  getById: (id: string) => apiClient.get(`/api/v1/users/${id}`),
  update: (id: string, payload: unknown) => apiClient.patch(`/api/v1/users/${id}`, payload),
};
