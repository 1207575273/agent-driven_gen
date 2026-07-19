import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";

export interface BarChartSeries {
  name: string;
  data: number[];
  type?: "bar" | "line";
  color?: string;
  yAxisIndex?: number;
}

export interface BarClickPayload {
  category: string;
  seriesName: string;
  value: number;
  dataIndex: number;
}

interface BarChartProps {
  categories: string[];
  series: BarChartSeries[];
  height?: number;
  stacked?: boolean;
  showLegend?: boolean;
  onBarClick?: (payload: BarClickPayload) => void;
}

const DARK_COLORS = ["#38bdf8", "#818cf8", "#6366f1", "#475569", "#1e293b", "#0ea5e9"];

export function BarChart({
  categories,
  series,
  height = 300,
  stacked = false,
  showLegend = true,
  onBarClick,
}: BarChartProps) {
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
      axisPointer: { type: "shadow" },
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
      axisLabel: { color: "#94a3b8", fontSize: 11, rotate: 0 },
      axisLine: { lineStyle: { color: "#1e293b" } },
      axisTick: { show: false },
    },
    yAxis: yAxes,
    series: series.map((s, idx) => ({
      type: s.type ?? "bar",
      name: s.name,
      data: s.data,
      yAxisIndex: s.yAxisIndex ?? 0,
      stack: stacked ? "total" : undefined,
      itemStyle: {
        color: s.color ?? DARK_COLORS[idx % DARK_COLORS.length],
        borderRadius: s.type === "line" ? undefined : [3, 3, 0, 0],
      },
      barMaxWidth: 48,
      lineStyle: s.type === "line" ? { color: s.color ?? "#f97316", width: 2 } : undefined,
      symbol: s.type === "line" ? "circle" : undefined,
      symbolSize: s.type === "line" ? 6 : undefined,
    })),
  };

  return (
    <ReactECharts
      option={option}
      style={{ height, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
      {...(onBarClick
        ? {
            onEvents: {
              click: (params: {
                componentType?: string;
                seriesName?: string;
                name?: string;
                value?: unknown;
                dataIndex?: number;
              }) => {
                if (params.componentType === "series" && params.dataIndex !== undefined) {
                  const cat = categories[params.dataIndex];
                  if (cat === undefined) return;
                  onBarClick({
                    category: cat,
                    seriesName: params.seriesName ?? "",
                    value: Number(params.value ?? 0),
                    dataIndex: params.dataIndex,
                  });
                }
              },
            },
          }
        : {})}
    />
  );
}
