import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { StructureItem } from "../../api/capacity";

interface PersonnelStructurePieChartProps {
  data: StructureItem[] | undefined;
  loading: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  正式: "#34d399",
  离职: "#f87171",
  兼岗: "#fbbf24",
  实习: "#60a5fa",
  顾问: "#a78bfa",
  外部: "#fb923c",
};

function getColor(status: string, index: number): string {
  return STATUS_COLORS[status] ?? `hsl(${(index * 60) % 360}, 60%, 50%)`;
}

export function PersonnelStructurePieChart({ data, loading }: PersonnelStructurePieChartProps) {
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
    tooltip: {
      trigger: "item",
      formatter: (params: unknown) => {
        const p = params as {
          name: string;
          value: number;
          percent: number;
          data: { person_count: number; total_days: number };
        };
        return `${p.name}<br/>人天: ${p.data.total_days.toLocaleString()}<br/>人数: ${p.data.person_count}<br/>占比: ${p.percent.toFixed(1)}%`;
      },
    },
    legend: {
      orient: "vertical",
      right: 10,
      top: "center",
      textStyle: { color: "#a3a3a3", fontSize: 12 },
    },
    series: [
      {
        type: "pie",
        radius: ["45%", "75%"],
        center: ["35%", "50%"],
        data: data.map((item, i) => ({
          name: item.employee_status,
          value: item.total_days,
          person_count: item.person_count,
          total_days: item.total_days,
          itemStyle: { color: getColor(item.employee_status, i) },
        })),
        label: {
          color: "#a3a3a3",
          fontSize: 11,
          formatter: (params) => {
            const p = params as { name: string; percent: number };
            return `${p.name}\n${p.percent.toFixed(1)}%`;
          },
        },
        emphasis: {
          label: { fontSize: 14, fontWeight: "bold" },
        },
        itemStyle: {
          borderColor: "#0d0d0d",
          borderWidth: 2,
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
