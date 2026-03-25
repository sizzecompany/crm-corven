import { apiClient } from './api-client';
export const agentService = {
  query: (message: string, context?: string) => apiClient.post('/api/v1/agent/query', { message, context }),
  logs: (skip = 0, limit = 20) => apiClient.get('/api/v1/agent/logs', { params: { skip, limit } }),
};
