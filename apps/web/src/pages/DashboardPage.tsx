import { MonthlyTrendChart } from "../components/dashboard/MonthlyTrendChart";
import { SummaryCards } from "../components/dashboard/SummaryCards";
import { useDashboardMonthlyTrend, useDashboardSummary } from "../hooks/useDashboard";

export default function DashboardPage() {
  const summary = useDashboardSummary();
  const trend = useDashboardMonthlyTrend();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-neutral-100">仪表盘</h1>
        <p className="mt-1 text-sm text-neutral-500">
          全局产能概览, 总人天 / 填报人数 / 项目数 / 部门数。
        </p>
      </div>

      <SummaryCards data={summary.data} loading={summary.isLoading} />

      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">月度总人天趋势</div>
        <MonthlyTrendChart data={trend.data} loading={trend.isLoading} />
      </div>
    </div>
  );
}
