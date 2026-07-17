import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { MonthlyTrendItem } from "../../api/capacity";

interface MonthlyTrendChartProps {
  data: MonthlyTrendItem[] | undefined;
  loading: boolean;
}

export function MonthlyTrendChart({ data, loading }: MonthlyTrendChartProps) {
  if (loading) {
    return (
      <div className="flex h-[320px] items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600">
        加载中...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-[320px] items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600">
        暂无数据
      </div>
    );
  }

  const option: EChartsOption = {
    grid: { left: 16, right: 24, top: 24, bottom: 32, containLabel: true },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (params: unknown) => {
        const p = (params as { axisValue: string; value: number }[])[0];
        if (!p) return "";
        return `${p.axisValue}<br/>总人天: ${p.value.toLocaleString()}`;
      },
    },
    xAxis: {
      type: "category",
      data: data.map((it) => it.month),
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
        data: data.map((it) => it.total_days),
        smooth: true,
        symbol: "circle",
        symbolSize: 6,
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
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: 320, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
    />
  );
}
