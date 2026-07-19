import type { MonthlyTrend } from "../../api/capacity";
import { useMonthlyTrend } from "../../hooks/useCapacity";
import { BarChart } from "../charts/BarChart";

export function MonthlyTrendChart() {
  const { data, isLoading, isError } = useMonthlyTrend();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-accent" />
      </div>
    );
  }

  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无月度趋势数据
      </div>
    );
  }

  const trendData: MonthlyTrend[] = data;

  const categories = trendData.map((item: MonthlyTrend) => {
    const parts = item.month.split("-");
    const monthNum = parts[1] ? Number.parseInt(parts[1], 10) : 0;
    return `${monthNum}月`;
  });

  const shouldSeries = trendData.map((item: MonthlyTrend) => item.should_be_days);
  const actualSeries = trendData.map((item: MonthlyTrend) => item.actual_days);
  const fillRateSeries = trendData.map((item: MonthlyTrend) => item.fill_rate);

  return (
    <BarChart
      categories={categories}
      series={[
        { name: "应有产能", data: shouldSeries, color: "#38bdf8" },
        { name: "实际产能", data: actualSeries, color: "#818cf8" },
        { name: "填报率(%)", data: fillRateSeries, type: "line", color: "#f97316", yAxisIndex: 1 },
      ]}
      height={320}
    />
  );
}
