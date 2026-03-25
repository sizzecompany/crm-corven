import { apiClient } from './api-client';
export const authService = {
  requestOtp: (email: string) => apiClient.post('/api/v1/auth/request-otp', { email }),
  verifyOtp: (email: string, code: string) => apiClient.post('/api/v1/auth/verify-otp', { email, code }),
  refresh: (refresh_token: string) => apiClient.post('/api/v1/auth/refresh', { refresh_token }),
  me: () => apiClient.get('/api/v1/auth/me'),
};
