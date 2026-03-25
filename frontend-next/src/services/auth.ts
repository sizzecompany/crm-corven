import { api } from './api';

export type RequestOtpPayload = { email: string };
export type RequestOtpResponse = { message: string; otp_code_dev_only?: string };

export type VerifyOtpPayload = { email: string; code: string };
export type VerifyOtpResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export const authApi = {
  requestOtp: (payload: RequestOtpPayload) => api.post<RequestOtpResponse>('/api/v1/auth/request-otp', payload),
  verifyOtp: (payload: VerifyOtpPayload) => api.post<VerifyOtpResponse>('/api/v1/auth/verify-otp', payload),
  refresh: (refresh_token: string) => api.post<VerifyOtpResponse>('/api/v1/auth/refresh', { refresh_token }),
  me: () => api.get('/api/v1/auth/me'),
};
