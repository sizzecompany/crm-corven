'use client';

import { useRouter } from 'next/navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  return (
    <>
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background/90 p-3 backdrop-blur">
        <strong>CRM Corven</strong>
        <button
          className="border border-border px-3 py-1 text-xs"
          onClick={() => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            document.cookie = 'access_token=; Max-Age=0; path=/';
            router.push('/auth/login');
          }}
        >
          Sair
        </button>
      </div>
      {children}
    </>
  );
}
