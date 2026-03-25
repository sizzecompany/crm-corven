import { apiClient } from './api-client';
export const documentsService = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/v1/documents/upload', formData);
  },
  list: () => apiClient.get('/api/v1/documents'),
  remove: (id: string) => apiClient.delete(`/api/v1/documents/${id}`),
};
