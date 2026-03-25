export function DataState({
  isLoading,
  isError,
  isEmpty,
  children,
}: {
  isLoading: boolean;
  isError: boolean;
  isEmpty: boolean;
  children: React.ReactNode;
}) {
  if (isLoading) return <div className="animate-pulse rounded bg-card p-4">Carregando (skeleton)...</div>;
  if (isError) return <div className="rounded border border-danger p-4 text-danger">Erro amigável ao buscar dados.</div>;
  if (isEmpty) return <div className="rounded border border-border p-4 text-muted">Nenhum dado encontrado (empty state).</div>;
  return <>{children}</>;
}
