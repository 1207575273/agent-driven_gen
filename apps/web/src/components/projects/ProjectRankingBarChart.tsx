import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { ProjectRankingItem } from "../../api/capacity";

interface ProjectRankingBarChartProps {
  data: ProjectRankingItem[] | undefined;
  loading: boolean;
}

export function ProjectRankingBarChart({ data, loading }: ProjectRankingBarChartProps) {
  if (loading) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600">
        加载中...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600">
        暂无数据
      </div>
    );
  }

  const top15 = data.slice(0, 15);
  const names = top15.map((it) => it.project_name);
  const values = top15.map((it) => it.total_days);

  const option: EChartsOption = {
    grid: { left: 16, right: 24, top: 16, bottom: 32, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: {
      type: "category",
      data: names,
      axisLabel: {
        color: "#a3a3a3",
        fontSize: 11,
        rotate: 30,
        interval: 0,
        formatter: (value: string) => {
          return value.length > 12 ? `${value.slice(0, 12)}...` : value;
        },
      },
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
        type: "bar",
        data: values,
        itemStyle: { color: "#34d399", borderRadius: [3, 3, 0, 0] },
        barMaxWidth: 40,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: 360, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
    />
  );
}
