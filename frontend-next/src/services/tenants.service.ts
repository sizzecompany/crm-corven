import { apiClient } from './api-client';
export const tenantsService = {
  list: (skip = 0, limit = 20) => apiClient.get('/api/v1/tenants', { params: { skip, limit } }),
  create: (payload: unknown) => apiClient.post('/api/v1/tenants', payload),
  update: (tenantId: string, payload: unknown) => apiClient.patch(`/api/v1/tenants/${tenantId}`, payload),
};
