import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { DepartmentOverview } from "../../api/capacity";
import { StatCard } from "../shared/StatCard";

interface DepartmentOverviewPanelProps {
  data: DepartmentOverview | undefined;
  loading: boolean;
}

export function DepartmentOverviewPanel({ data, loading }: DepartmentOverviewPanelProps) {
  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-neutral-600">
        加载中...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-neutral-600">
        请先选择部门
      </div>
    );
  }

  // 项目分布饼图
  const pieOption: EChartsOption = {
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    tooltip: {
      trigger: "item",
      formatter: (params: unknown) => {
        const p = params as { name: string; value: number; percent: number };
        return `${p.name}: ${p.value.toFixed(1)} 人天 (${p.percent.toFixed(1)}%)`;
      },
    },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        center: ["50%", "50%"],
        data: data.project_distribution.map((it) => ({
          name: it.project_name,
          value: it.total_days,
        })),
        label: {
          color: "#a3a3a3",
          fontSize: 10,
          formatter: (params) => {
            const p = params as { name: string; percent: number };
            return `${p.name.length > 10 ? `${p.name.slice(0, 10)}...` : p.name}\n${p.percent.toFixed(1)}%`;
          },
        },
        emphasis: {
          label: { fontSize: 13, fontWeight: "bold" },
        },
        itemStyle: {
          borderColor: "#0d0d0d",
          borderWidth: 2,
        },
      },
    ],
  };

  return (
    <div className="space-y-5">
      {/* KPIs */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard title="总人天" value={data.total_person_days.toLocaleString()} unit="人天" />
        <StatCard title="人均人天" value={data.avg_person_days.toFixed(1)} unit="人天" />
        <StatCard title="人数" value={data.member_count} unit="人" />
      </div>

      {/* 集中度 */}
      <div className="flex gap-6 text-sm">
        <span className="text-neutral-500">
          Top 3 集中度:{" "}
          <span className="font-mono text-neutral-100">
            {data.top_n_concentration.top3_percentage.toFixed(1)}%
          </span>
        </span>
        <span className="text-neutral-500">
          Top 5 集中度:{" "}
          <span className="font-mono text-neutral-100">
            {data.top_n_concentration.top5_percentage.toFixed(1)}%
          </span>
        </span>
      </div>

      {/* PIE */}
      <div>
        <div className="mb-3 text-sm text-neutral-400">项目分布</div>
        {data.project_distribution.length > 0 ? (
          <ReactECharts
            option={pieOption}
            style={{ height: 300, width: "100%" }}
            opts={{ renderer: "svg" }}
            notMerge
          />
        ) : (
          <div className="flex h-48 items-center justify-center text-sm text-neutral-600">
            暂无项目分布数据
          </div>
        )}
      </div>
    </div>
  );
}
