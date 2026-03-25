'use client';

import { useQuery } from '@tanstack/react-query';
import { PageShell } from '@/components/layout/page-shell';
import { DataState } from '@/components/ui/data-state';

export function ModulePage({
  title,
  description,
  queryKey,
  queryFn,
  children,
}: {
  title: string;
  description: string;
  queryKey: string[];
  queryFn: () => Promise<unknown>;
  children?: React.ReactNode;
}) {
  const query = useQuery({ queryKey, queryFn });

  return (
    <PageShell title={title} description={description}>
      <DataState
        isLoading={query.isLoading}
        isError={query.isError}
        isEmpty={Array.isArray((query.data as any)?.data) && (query.data as any).data.length === 0}
      >
        <pre className="rounded bg-card p-4 text-xs overflow-x-auto">{JSON.stringify((query.data as any)?.data ?? {}, null, 2)}</pre>
      </DataState>
      {children}
    </PageShell>
  );
}
