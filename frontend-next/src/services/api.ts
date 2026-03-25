import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
const AUTH_PREFIX = '/api/v1/auth';

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

type RefreshResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (typeof window === 'undefined') return Promise.reject(error);

    const originalRequest = error.config as RetryConfig | undefined;
    const status = error.response?.status;
    const url = originalRequest?.url ?? '';

    if (!originalRequest || status !== 401 || originalRequest._retry || url.startsWith(AUTH_PREFIX)) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      localStorage.removeItem('access_token');
      window.location.href = '/auth/login';
      return Promise.reject(error);
    }

    try {
      originalRequest._retry = true;

      const refreshResponse = await axios.post<RefreshResponse>(
        `${API_BASE_URL}/api/v1/auth/refresh`,
        { refresh_token: refreshToken }
      );

      const { access_token, refresh_token } = refreshResponse.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      document.cookie = `access_token=${access_token}; path=/`;

      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return api(originalRequest);
    } catch (refreshError) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      document.cookie = 'access_token=; Max-Age=0; path=/';
      window.location.href = '/auth/login';
      return Promise.reject(refreshError);
    }
  }
);
