import { apiClient } from './api-client';
export const healthService = {
  check: () => apiClient.get('/health'),
};
