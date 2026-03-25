import { apiClient } from './api-client';
export const settingsService = {
  profile: () => apiClient.get('/api/v1/settings/profile'),
  updateProfile: (payload: unknown) => apiClient.patch('/api/v1/settings/profile', payload),
  company: () => apiClient.get('/api/v1/settings/company'),
  updateCompany: (payload: unknown) => apiClient.patch('/api/v1/settings/company', payload),
  integrations: () => apiClient.get('/api/v1/settings/integrations'),
};
