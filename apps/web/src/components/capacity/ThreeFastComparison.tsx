import type { ThreeFastComparisonItem } from "../../api/capacity";
import { useThreeFastComparison } from "../../hooks/useCapacity";
import { BarChart, type BarChartSeries } from "../charts/BarChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";

/** 计划=浅灰蓝, 实际=亮蓝 — 全局配对色, 与品类无关(品类靠 X 轴标签区分) */
const PLAN_COLOR = "#475569";
const ACTUAL_COLOR = "#38bdf8";

/** 品类固定顺序 */
const CATEGORY_ORDER = ["快服务", "快交付", "快营销"];

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

  // 按季度分组, 每季度一张图; X 轴 = 品类, 两根柱(计划/实际)
  const quarters = [...new Set(items.map((d) => d.quarter))].sort();

  const charts = quarters.map((q) => {
    const cats = CATEGORY_ORDER.filter((cat) =>
      items.some((d) => d.quarter === q && d.category_name === cat),
    );
    // 补回数据里存在但不在 ORDER 中的品类
    for (const it of items) {
      if (it.quarter === q && !cats.includes(it.category_name)) {
        cats.push(it.category_name);
      }
    }

    const planSeries: BarChartSeries = {
      name: "计划",
      color: PLAN_COLOR,
      data: cats.map((cat) => {
        const it = items.find((d) => d.quarter === q && d.category_name === cat);
        return it?.plan_days ?? 0;
      }),
      type: "bar",
    };
    const actualSeries: BarChartSeries = {
      name: "实际",
      color: ACTUAL_COLOR,
      data: cats.map((cat) => {
        const it = items.find((d) => d.quarter === q && d.category_name === cat);
        return it?.actual_days ?? 0;
      }),
      type: "bar",
    };

    return { quarter: q, categories: cats, series: [planSeries, actualSeries] };
  });

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">三快计划 vs 实际(按季度)</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {charts.map((c) => (
            <div
              key={c.quarter}
              className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4"
            >
              <div className="text-sm font-medium text-neutral-300 mb-2">{c.quarter}</div>
              <BarChart categories={c.categories} series={c.series} height={280} showLegend />
            </div>
          ))}
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
