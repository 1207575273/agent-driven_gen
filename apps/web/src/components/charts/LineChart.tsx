import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";

export interface LineSeries {
  name: string;
  data: number[];
  color?: string;
  areaStyle?: boolean;
  yAxisIndex?: number;
}

interface LineChartProps {
  categories: string[];
  series: LineSeries[];
  height?: number;
  showLegend?: boolean;
  markAreas?: Array<{
    name: string;
    start: number; // category index (0-based)
    end: number; // category index
    color?: string;
  }>;
}

const DARK_COLORS = ["#38bdf8", "#818cf8", "#f97316", "#22d3ee", "#a78bfa"];

export function LineChart({
  categories,
  series,
  height = 300,
  showLegend = true,
  markAreas,
}: LineChartProps) {
  if (categories.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600"
        style={{ height }}
      >
        暂无数据
      </div>
    );
  }

  const yAxes: EChartsOption["yAxis"] = [];
  let hasDualAxis = false;
  for (const s of series) {
    if (s.yAxisIndex !== undefined && s.yAxisIndex > 0) {
      hasDualAxis = true;
    }
  }

  if (hasDualAxis) {
    yAxes.push(
      {
        type: "value",
        name: "人天",
        nameTextStyle: { color: "#64748b", fontSize: 10 },
        axisLabel: { color: "#94a3b8", fontSize: 11 },
        splitLine: { lineStyle: { color: "#1e293b" } },
      },
      {
        type: "value",
        name: "%",
        min: 0,
        max: 150,
        nameTextStyle: { color: "#64748b", fontSize: 10 },
        axisLabel: { color: "#94a3b8", fontSize: 11, formatter: "{value}%" },
        splitLine: { show: false },
      },
    );
  } else {
    yAxes.push({
      type: "value",
      axisLabel: { color: "#94a3b8", fontSize: 11 },
      splitLine: { lineStyle: { color: "#1e293b" } },
    });
  }

  const option: EChartsOption = {
    backgroundColor: "transparent",
    textStyle: { color: "#94a3b8" },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(15,23,42,0.9)",
      borderColor: "#1e293b",
      textStyle: { color: "#e2e8f0" },
    },
    legend: showLegend
      ? {
          top: 0,
          textStyle: { color: "#94a3b8", fontSize: 11 },
        }
      : undefined,
    grid: { left: 16, right: hasDualAxis ? 60 : 16, top: showLegend ? 30 : 16, bottom: 24 },
    xAxis: {
      type: "category",
      data: categories,
      axisLabel: { color: "#94a3b8", fontSize: 11 },
      axisLine: { lineStyle: { color: "#1e293b" } },
      axisTick: { show: false },
    },
    yAxis: yAxes,
    series: series.map((s, idx) => ({
      type: "line",
      name: s.name,
      data: s.data,
      yAxisIndex: s.yAxisIndex ?? 0,
      smooth: true,
      lineStyle: { color: s.color ?? DARK_COLORS[idx % DARK_COLORS.length], width: 2 },
      itemStyle: { color: s.color ?? DARK_COLORS[idx % DARK_COLORS.length] },
      symbol: "circle",
      symbolSize: 6,
      areaStyle: s.areaStyle
        ? {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: `${s.color ?? DARK_COLORS[idx % DARK_COLORS.length]}33` },
                { offset: 1, color: `${s.color ?? DARK_COLORS[idx % DARK_COLORS.length]}05` },
              ],
            },
          }
        : undefined,
      markArea: markAreas
        ? {
            silent: true,
            itemStyle: {
              color: "rgba(56,189,248,0.06)",
            },
            data: markAreas.map((area) => [{ xAxis: area.start }, { xAxis: area.end }]),
            label: {
              show: true,
              position: "insideTop",
              color: "#64748b",
              fontSize: 10,
            },
          }
        : undefined,
    })),
  };

  return (
    <ReactECharts
      option={option}
      style={{ height, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
    />
  );
}
