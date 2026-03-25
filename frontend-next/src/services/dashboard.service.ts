import { apiClient } from './api-client';
export const dashboardService = {
  admin: () => apiClient.get('/api/v1/dashboard/admin'),
  user: () => apiClient.get('/api/v1/dashboard/user'),
};
