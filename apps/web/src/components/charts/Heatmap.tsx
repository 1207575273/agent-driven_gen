import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";

export interface HeatmapCellClickPayload {
  xLabel: string;
  yLabel: string;
  value: number;
  xIndex: number;
  yIndex: number;
}

interface HeatmapProps {
  xLabels: string[];
  yLabels: string[];
  data: number[][];
  height?: number;
  unit?: string;
  onCellClick?: (payload: HeatmapCellClickPayload) => void;
}

const HEAT_COLORS = ["#060b14", "#1e3a5f", "#2563eb", "#38bdf8", "#7dd3fc"];

export function Heatmap({
  xLabels,
  yLabels,
  data,
  height = 360,
  unit = "人天",
  onCellClick,
}: HeatmapProps) {
  if (xLabels.length === 0 || yLabels.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600"
        style={{ height }}
      >
        暂无数据
      </div>
    );
  }

  // Flatten matrix into [xIdx, yIdx, value] tuples
  const flatData: [number, number, number][] = [];
  for (let yi = 0; yi < yLabels.length; yi++) {
    for (let xi = 0; xi < xLabels.length; xi++) {
      const value = data[yi]?.[xi] ?? 0;
      flatData.push([xi, yi, value]);
    }
  }

  const maxVal = Math.max(...flatData.map((d) => d[2]), 1);

  const option: EChartsOption = {
    backgroundColor: "transparent",
    textStyle: { color: "#94a3b8" },
    tooltip: {
      position: "top",
      backgroundColor: "rgba(15,23,42,0.9)",
      borderColor: "#1e293b",
      textStyle: { color: "#e2e8f0" },
      formatter: (params: unknown) => {
        const p = params as { value: [number, number, number] };
        const xi = p.value[0];
        const yi = p.value[1];
        const v = p.value[2];
        return `${xLabels[xi]} - ${yLabels[yi]}<br/>${v.toFixed(1)} ${unit}`;
      },
    },
    grid: { left: 80, right: 40, top: 16, bottom: 60 },
    xAxis: {
      type: "category",
      data: xLabels,
      position: "bottom",
      axisLabel: {
        color: "#94a3b8",
        fontSize: 11,
        rotate: xLabels.length > 6 ? 30 : 0,
      },
      axisLine: { lineStyle: { color: "#1e293b" } },
      axisTick: { show: false },
      splitArea: { show: true },
    },
    yAxis: {
      type: "category",
      data: yLabels,
      axisLabel: { color: "#94a3b8", fontSize: 11 },
      axisLine: { lineStyle: { color: "#1e293b" } },
      axisTick: { show: false },
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: maxVal,
      calculable: true,
      orient: "vertical",
      right: 4,
      top: "center",
      text: [maxVal.toFixed(0), "0"],
      textStyle: { color: "#94a3b8", fontSize: 10 },
      inRange: {
        color: HEAT_COLORS,
      },
      itemHeight: 160,
    },
    series: [
      {
        type: "heatmap",
        data: flatData,
        label: {
          show: true,
          color: "#cbd5e1",
          fontSize: 11,
          formatter: (p: unknown) => {
            const v = (p as { value: [number, number, number] }).value[2];
            return v > 0 ? v.toFixed(1) : "";
          },
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: "rgba(56,189,248,0.5)",
            borderColor: "#38bdf8",
            borderWidth: 1,
          },
        },
        itemStyle: {
          borderColor: "#060b14",
          borderWidth: 2,
          borderRadius: 2,
        },
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
      {...(onCellClick
        ? {
            onEvents: {
              click: (params: {
                componentType?: string;
                componentSubType?: string;
                value?: unknown;
              }) => {
                if (params.componentSubType === "heatmap" && Array.isArray(params.value)) {
                  const v = params.value as [number, number, number];
                  const xl = xLabels[v[0]];
                  const yl = yLabels[v[1]];
                  if (xl === undefined || yl === undefined) return;
                  onCellClick({
                    xLabel: xl,
                    yLabel: yl,
                    value: v[2],
                    xIndex: v[0],
                    yIndex: v[1],
                  });
                }
              },
            },
          }
        : {})}
    />
  );
}
