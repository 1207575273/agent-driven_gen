interface StatCardProps {
  title: string;
  value: number | string;
  unit?: string;
  loading?: boolean;
}

export function StatCard({ title, value, unit, loading = false }: StatCardProps) {
  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900/60 px-5 py-4">
      <div className="mb-1 text-xs text-neutral-500">{title}</div>
      {loading ? (
        <div className="h-8 w-20 animate-pulse rounded bg-neutral-800" />
      ) : (
        <div className="flex items-baseline gap-1">
          <span className="font-mono text-2xl font-semibold tabular-nums text-neutral-50">
            {value}
          </span>
          {unit ? <span className="text-sm text-neutral-500">{unit}</span> : null}
        </div>
      )}
    </div>
  );
}
