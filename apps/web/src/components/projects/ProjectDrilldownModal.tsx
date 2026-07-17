import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import { useEffect } from "react";
import type { MonthlyTrendItem } from "../../api/capacity";
import { useProjectMembers, useProjectMonthlyTrend } from "../../hooks/useProjects";
import { MemberDetailTable } from "./MemberDetailTable";

interface ProjectDrilldownModalProps {
  projectName: string | null;
  onClose: () => void;
}

export function ProjectDrilldownModal({ projectName, onClose }: ProjectDrilldownModalProps) {
  const members = useProjectMembers(projectName);
  const trend = useProjectMonthlyTrend(projectName);

  // 按 Escape 关闭
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [onClose]);

  if (!projectName) return null;

  const trendOption: EChartsOption | null =
    trend.data && trend.data.length > 0
      ? {
          grid: { left: 16, right: 24, top: 24, bottom: 32, containLabel: true },
          tooltip: { trigger: "axis" },
          xAxis: {
            type: "category",
            data: trend.data.map((it: MonthlyTrendItem) => it.month),
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
          series: [
            {
              type: "line",
              data: trend.data.map((it: MonthlyTrendItem) => it.total_days),
              smooth: true,
              lineStyle: { color: "#34d399", width: 2 },
              itemStyle: { color: "#34d399" },
              areaStyle: {
                color: {
                  type: "linear",
                  x: 0,
                  y: 0,
                  x2: 0,
                  y2: 1,
                  colorStops: [
                    { offset: 0, color: "rgba(52, 211, 153, 0.15)" },
                    { offset: 1, color: "rgba(52, 211, 153, 0.01)" },
                  ],
                },
              },
            },
          ],
        }
      : null;

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center">
      {/* 遮罩 */}
      <button
        type="button"
        className="absolute inset-0 bg-black/60 cursor-default"
        onClick={onClose}
        aria-label="关闭"
      />

      {/* 内容 */}
      <div className="relative z-10 max-h-[85vh] w-[900px] overflow-y-auto rounded-lg border border-neutral-800 bg-[#0d0d0d] shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-neutral-800 bg-[#0d0d0d] px-6 py-4">
          <h2 className="text-lg font-semibold text-neutral-100">项目: {projectName}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md px-3 py-1.5 text-sm text-neutral-500 transition-colors hover:bg-neutral-800 hover:text-neutral-200"
          >
            关闭 (Esc)
          </button>
        </div>

        <div className="space-y-6 p-6">
          {/* 人员明细 */}
          <div>
            <h3 className="mb-3 text-sm font-medium text-neutral-400">人员投入明细</h3>
            <MemberDetailTable data={members.data} loading={members.isLoading} />
          </div>

          {/* 月度趋势 */}
          {trendOption ? (
            <div>
              <h3 className="mb-3 text-sm font-medium text-neutral-400">月度趋势</h3>
              <ReactECharts
                option={trendOption}
                style={{ height: 280, width: "100%" }}
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
