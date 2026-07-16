import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { Item } from "../api/client";

interface QuantityChartProps {
  items: Item[];
}

// 各 Item 的数量柱图 —— 数据全部来自左侧真实列表, 增删改会实时反映, 不是填充用的假图。
export function QuantityChart({ items }: QuantityChartProps) {
  if (items.length === 0) {
    return (
      <div className="flex h-[240px] items-center justify-center rounded-lg border border-dashed border-neutral-800 text-sm text-neutral-600">
        暂无数据, 新增一条即可看到柱图
      </div>
    );
  }

  const option: EChartsOption = {
    grid: { left: 8, right: 16, top: 16, bottom: 24, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: {
      type: "category",
      data: items.map((it) => it.name),
      axisLabel: { color: "#a3a3a3", fontSize: 11, interval: 0 },
      axisLine: { lineStyle: { color: "#404040" } },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: { color: "#a3a3a3", fontSize: 11 },
      splitLine: { lineStyle: { color: "#1f1f1f" } },
    },
    series: [
      {
        type: "bar",
        data: items.map((it) => it.quantity),
        itemStyle: { color: "#34d399", borderRadius: [3, 3, 0, 0] },
        barMaxWidth: 36,
      },
    ],
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: 240, width: "100%" }}
      opts={{ renderer: "svg" }}
      notMerge
    />
  );
}
