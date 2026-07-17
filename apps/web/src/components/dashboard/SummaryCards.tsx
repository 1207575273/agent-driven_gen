import type { SummaryResponse } from "../../api/capacity";
import { StatCard } from "../shared/StatCard";

interface SummaryCardsProps {
  data: SummaryResponse | undefined;
  loading: boolean;
}

export function SummaryCards({ data, loading }: SummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="总人天"
        value={data ? data.total_person_days.toLocaleString() : "—"}
        unit="人天"
        loading={loading}
      />
      <StatCard
        title="填报人数"
        value={data ? data.reporter_count : "—"}
        unit="人"
        loading={loading}
      />
      <StatCard
        title="项目数"
        value={data ? data.project_count : "—"}
        unit="个"
        loading={loading}
      />
      <StatCard
        title="部门数"
        value={data ? data.department_count : "—"}
        unit="个"
        loading={loading}
      />
    </div>
  );
}
