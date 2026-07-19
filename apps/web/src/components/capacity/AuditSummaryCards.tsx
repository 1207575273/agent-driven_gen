import { useAuditSummary } from "../../hooks/useCapacity";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { StatCard } from "../shared/StatCard";

export function AuditSummaryCards() {
  const { data, isLoading, isError } = useAuditSummary();

  if (isLoading) return <LoadingSpinner />;

  if (isError || !data) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载汇总数据失败
      </div>
    );
  }

  const fillRateAlert = data.fill_rate < 80;
  const fillRateDanger = data.fill_rate < 60;
  const deviationNegative = data.deviation < 0;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="应有产能合计"
        value={`${data.should_be_days.toFixed(1)} 人天`}
        subtitle={`${data.employee_count} 人`}
      />
      <StatCard title="实际产能合计" value={`${data.actual_days.toFixed(1)} 人天`} />
      <StatCard
        title="整体填报率"
        value={`${data.fill_rate.toFixed(1)}%`}
        alert={fillRateAlert}
        danger={fillRateDanger}
      />
      <StatCard
        title="偏差合计"
        value={`${data.deviation >= 0 ? "+" : ""}${data.deviation.toFixed(1)} 人天`}
        danger={data.deviation < -500}
        alert={deviationNegative}
        subtitle={`零填报 ${data.zero_fill_count} / 异常 ${data.abnormal_count}`}
      />
    </div>
  );
}
