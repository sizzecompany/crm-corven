'use client';

import { useQuery } from '@tanstack/react-query';
import { authService } from '@/services/auth.service';

export function useAuthMe() {
  return useQuery({ queryKey: ['auth', 'me'], queryFn: () => authService.me() });
}
