import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";

export interface PieClickPayload {
  name: string;
  value: number;
  percent: number;
  category_id?: number;
}

interface PieChartProps {
  data: Array<{ name: string; value: number; category_id?: number }>;
  height?: number;
  innerRadius?: string; // "0" = pie, "40%" = ring
  showLabel?: boolean;
  onSliceClick?: (payload: PieClickPayload) => void;
}

const DARK_COLORS = ["#38bdf8", "#818cf8", "#6366f1", "#475569", "#1e293b", "#0ea5e9", "#a78bfa"];

export function PieChart({
  data,
  height = 300,
  innerRadius = "40%",
  showLabel = true,
  onSliceClick,
}: PieChartProps) {
  if (data.length === 0) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600"
        style={{ height }}
      >
        暂无数据
      </div>
    );
  }

  const option: EChartsOption = {
    backgroundColor: "transparent",
    textStyle: { color: "#94a3b8" },
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} 人天 ({d}%)",
      backgroundColor: "rgba(15,23,42,0.9)",
      borderColor: "#1e293b",
      textStyle: { color: "#e2e8f0" },
    },
    legend: showLabel
      ? {
          orient: "vertical",
          right: 10,
          top: "center",
          textStyle: { color: "#94a3b8", fontSize: 11 },
        }
      : undefined,
    series: [
      {
        type: "pie",
        radius: ["30%", innerRadius],
        center: showLabel ? ["35%", "50%"] : ["50%", "50%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderColor: "#060b14",
          borderWidth: 2,
        },
        label: showLabel
          ? {
              show: true,
              position: "outside",
              formatter: "{b}\n{d}%",
              color: "#94a3b8",
              fontSize: 11,
            }
          : {
              show: true,
              position: "inside",
              formatter: "{d}%",
              color: "#e2e8f0",
              fontSize: 12,
            },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: "bold" },
          scaleSize: 8,
        },
        data: data.map((item, idx) => ({
          ...item,
          itemStyle: { color: DARK_COLORS[idx % DARK_COLORS.length] },
        })),
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
      {...(onSliceClick
        ? {
            onEvents: {
              click: (params: {
                componentType?: string;
                name?: string;
                value?: unknown;
                percent?: number;
                data?: Record<string, unknown>;
              }) => {
                if (params.componentType === "series") {
                  onSliceClick({
                    name: params.name ?? "",
                    value: Number(params.value ?? 0),
                    percent: Number(params.percent ?? 0),
                    category_id: params.data?.category_id as number | undefined,
                  });
                }
              },
            },
          }
        : {})}
    />
  );
}
