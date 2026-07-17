import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import { useEffect } from "react";
import type { MemberProjectItem } from "../../api/capacity";
import { useMemberProjects } from "../../hooks/useDepartments";

interface MemberDrilldownModalProps {
  employeeId: number | null;
  employeeName: string;
  onClose: () => void;
}

export function MemberDrilldownModal({
  employeeId,
  employeeName,
  onClose,
}: MemberDrilldownModalProps) {
  const { data, isLoading } = useMemberProjects(employeeId);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  if (employeeId === null) return null;

  const items: MemberProjectItem[] = data ?? [];

  // 月度分布堆叠图
  const allMonths = new Set<string>();
  for (const proj of items) {
    for (const m of proj.monthly_breakdown) {
      allMonths.add(m.month);
    }
  }
  const months = Array.from(allMonths).sort();

  const seriesData = items.map((proj) => ({
    name: proj.project_name,
    type: "bar" as const,
    stack: "total",
    emphasis: { focus: "series" as const },
    data: months.map((month) => {
      const found = proj.monthly_breakdown.find((m) => m.month === month);
      return found ? found.days : 0;
    }),
  }));

  const chartOption: EChartsOption | null =
    items.length > 0 && months.length > 0
      ? {
          grid: { left: 16, right: 24, top: 24, bottom: 32, containLabel: true },
          tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
          legend: {
            data: items.map((p) => p.project_name),
            orient: "horizontal",
            top: 0,
            textStyle: { color: "#a3a3a3", fontSize: 11 },
          },
          xAxis: {
            type: "category",
            data: months,
            axisLabel: { color: "#a3a3a3", fontSize: 12 },
            axisLine: { lineStyle: { color: "#404040" } },
            axisTick: { show: false },
          },
          yAxis: {
            type: "value",
            name: "人天",
            nameTextStyle: { color: "#a3a3a3", fontSize: 12 },
            axisLabel: { color: "#a3a3a3", fontSize: 12 },
            splitLine: { lineStyle: { color: "#1f1f1f" } },
          },
          series: seriesData,
        }
      : null;

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center">
      <button
        type="button"
        className="absolute inset-0 bg-black/60 cursor-default"
        onClick={onClose}
        aria-label="关闭"
      />
      <div className="relative z-10 max-h-[85vh] w-[800px] overflow-y-auto rounded-lg border border-neutral-800 bg-[#0d0d0d] shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-neutral-800 bg-[#0d0d0d] px-6 py-4">
          <h2 className="text-lg font-semibold text-neutral-100">人员: {employeeName}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-3 py-1.5 text-sm text-neutral-500 transition-colors hover:bg-neutral-800 hover:text-neutral-200"
          >
            关闭 (Esc)
          </button>
        </div>

        <div className="space-y-6 p-6">
          {/* 项目明细表格 */}
          <div>
            <h3 className="mb-3 text-sm font-medium text-neutral-400">项目投入明细</h3>
            {isLoading ? (
              <div className="flex h-32 items-center justify-center text-sm text-neutral-600">
                加载中...
              </div>
            ) : items.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-sm text-neutral-600">
                暂无项目数据
              </div>
            ) : (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-neutral-800">
                    <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">
                      项目名
                    </th>
                    <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">
                      总人天
                    </th>
                    <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">
                      月度分布
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((proj) => (
                    <tr key={proj.project_name} className="border-b border-neutral-900">
                      <td className="px-4 py-3 text-sm text-neutral-100">{proj.project_name}</td>
                      <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                        {proj.total_days.toFixed(1)}
                      </td>
                      <td className="px-4 py-3 text-sm text-neutral-500">
                        {proj.monthly_breakdown
                          .map((m) => `${m.month}: ${m.days.toFixed(1)}`)
                          .join(" / ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* 月度分布堆叠柱状图 */}
          {chartOption ? (
            <div>
              <h3 className="mb-3 text-sm font-medium text-neutral-400">月度分布</h3>
              <ReactECharts
                option={chartOption}
                style={{ height: 300, width: "100%" }}
                opts={{ renderer: "svg" }}
                notMerge
              />
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
