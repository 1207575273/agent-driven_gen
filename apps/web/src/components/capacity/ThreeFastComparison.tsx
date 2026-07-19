import type { ThreeFastComparisonItem } from "../../api/capacity";
import { useThreeFastComparison } from "../../hooks/useCapacity";
import { BarChart } from "../charts/BarChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";

export function ThreeFastComparison() {
  const { data, isLoading, isError } = useThreeFastComparison();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无三快计划数据
      </div>
    );
  }

  const items: ThreeFastComparisonItem[] = data;

  const quarters = [...new Set(items.map((d: ThreeFastComparisonItem) => d.quarter))];
  const categories = [...new Set(items.map((d: ThreeFastComparisonItem) => d.category_name))];

  const planSeries = categories.map((cat: string) => ({
    name: `${cat}-计划`,
    data: quarters.map((q: string) => {
      const item = items.find(
        (d: ThreeFastComparisonItem) => d.quarter === q && d.category_name === cat,
      );
      return item?.plan_days ?? 0;
    }),
    color: "#475569",
    type: "bar" as const,
  }));

  const actualSeries = categories.map((cat: string) => ({
    name: `${cat}-实际`,
    data: quarters.map((q: string) => {
      const item = items.find(
        (d: ThreeFastComparisonItem) => d.quarter === q && d.category_name === cat,
      );
      return item?.actual_days ?? 0;
    }),
    type: "bar" as const,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">Q1/Q2 三快计划 vs 实际</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <BarChart categories={quarters} series={[...planSeries, ...actualSeries]} height={320} />
        </div>
      </div>

      <ThreeFastDetailTable data={items} />
    </div>
  );
}

function ThreeFastDetailTable({ data }: { data: ThreeFastComparisonItem[] }) {
  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">详细对比</h3>
      <div className="rounded-lg border border-neutral-800/50 overflow-hidden">
        <table className="min-w-full">
          <thead>
            <tr className="bg-neutral-900/50">
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                季度
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                分类
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                计划
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                实际
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                偏差
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                达成率
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr
                key={`${item.quarter}-${item.category_id}-${idx}`}
                className="border-t border-neutral-800/50"
              >
                <td className="px-3 py-2.5 text-sm text-neutral-200">{item.quarter}</td>
                <td className="px-3 py-2.5 text-sm text-neutral-200">{item.category_name}</td>
                <td className="px-3 py-2.5 text-sm text-neutral-300 text-right">
                  {item.plan_days.toFixed(1)}
                </td>
                <td className="px-3 py-2.5 text-sm text-neutral-200 text-right">
                  {item.actual_days.toFixed(1)}
                </td>
                <td className="px-3 py-2.5 text-sm text-right">
                  <span className={item.deviation < 0 ? "text-red-400" : "text-emerald-400"}>
                    {item.deviation >= 0 ? "+" : ""}
                    {item.deviation.toFixed(1)}
                  </span>
                </td>
                <td className="px-3 py-2.5 text-sm text-right">
                  <span
                    className={
                      item.achieve_rate >= 100
                        ? "text-emerald-400"
                        : item.achieve_rate >= 90
                          ? "text-amber-400"
                          : "text-red-400"
                    }
                  >
                    {item.achieve_rate.toFixed(1)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
