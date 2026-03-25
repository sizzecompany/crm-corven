import { apiClient } from './api-client';
export const whatsappService = {
  createInstance: (payload: unknown) => apiClient.post('/api/v1/whatsapp/instances', payload),
  listInstances: () => apiClient.get('/api/v1/whatsapp/instances'),
  getStatus: (id: string) => apiClient.get(`/api/v1/whatsapp/instances/${id}/status`),
  send: (payload: unknown) => apiClient.post('/api/v1/whatsapp/send', payload),
  messages: (skip = 0, limit = 20) => apiClient.get('/api/v1/whatsapp/messages', { params: { skip, limit } }),
  byLead: (leadId: string, skip = 0, limit = 20) => apiClient.get(`/api/v1/whatsapp/messages/${leadId}`, { params: { skip, limit } }),
};
