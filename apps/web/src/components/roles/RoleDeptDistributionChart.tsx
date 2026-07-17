import type { EChartsOption } from "echarts";
import ReactECharts from "echarts-for-react";
import type { RoleAggregationItem } from "../../api/capacity";

interface RoleDeptDistributionChartProps {
  data: RoleAggregationItem[] | undefined;
  loading: boolean;
}

export function RoleDeptDistributionChart({ data, loading }: RoleDeptDistributionChartProps) {
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

  // 收集所有部门名
  const deptSet = new Set<string>();
  for (const role of data) {
    for (const d of role.dept_distribution) {
      deptSet.add(d.department);
    }
  }
  const depts = Array.from(deptSet);

  const roles = data.map((r) => r.role);

  const series = depts.map((dept) => ({
    name: dept,
    type: "bar" as const,
    stack: "total",
    emphasis: { focus: "series" as const },
    data: data.map((role) => {
      const found = role.dept_distribution.find((d) => d.department === dept);
      return found ? found.person_count : 0;
    }),
  }));

  const option: EChartsOption = {
    grid: { left: 16, right: 24, top: 24, bottom: 32, containLabel: true },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
    },
    legend: {
      data: depts,
      orient: "horizontal",
      top: 0,
      textStyle: { color: "#a3a3a3", fontSize: 11 },
    },
    xAxis: {
      type: "category",
      data: roles,
      axisLabel: { color: "#a3a3a3", fontSize: 12 },
      axisLine: { lineStyle: { color: "#404040" } },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      name: "人数",
      nameTextStyle: { color: "#a3a3a3", fontSize: 12 },
      axisLabel: { color: "#a3a3a3", fontSize: 12 },
      splitLine: { lineStyle: { color: "#1f1f1f" } },
    },
    series,
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
