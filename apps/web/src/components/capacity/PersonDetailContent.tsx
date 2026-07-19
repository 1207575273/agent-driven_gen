import type { PersonMonthlyData, PersonProjectItem } from "../../api/capacity";
import { usePersonMonthly, usePersonProjects } from "../../hooks/useCapacity";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";

interface PersonDetailContentProps {
  employeeId: number;
  employeeName: string;
  timePeriod?: string;
}

export function PersonDetailContent({
  employeeId,
  employeeName,
  timePeriod,
}: PersonDetailContentProps) {
  const { data: monthlyData, isLoading: monthlyLoading } = usePersonMonthly(employeeId);
  const { data: projectsData, isLoading: projectsLoading } = usePersonProjects(
    employeeId,
    timePeriod ?? undefined,
  );

  const monthlyColumns: Column<PersonMonthlyData>[] = [
    { key: "month", title: "月度", dataIndex: "month" },
    {
      key: "should_be_days",
      title: "应有产能",
      dataIndex: "should_be_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "actual_days",
      title: "实际产能",
      dataIndex: "actual_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "deviation",
      title: "偏差",
      dataIndex: "deviation",
      align: "right",
      render: (v) => {
        const num = Number(v);
        const formatted = Number.isNaN(num) ? "-" : `${num >= 0 ? "+" : ""}${num.toFixed(1)}`;
        return <span className={num < 0 ? "text-red-400" : "text-emerald-400"}>{formatted}</span>;
      },
    },
    {
      key: "fill_rate",
      title: "填报率",
      dataIndex: "fill_rate",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : `${num.toFixed(1)}%`;
      },
    },
  ];

  const projectColumns: Column<PersonProjectItem>[] = [
    { key: "project_name", title: "项目名称", dataIndex: "project_name" },
    { key: "category_path", title: "分类路径", dataIndex: "category_path" },
    {
      key: "person_days",
      title: "人天",
      dataIndex: "person_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
  ];

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">{employeeName} — 月度产能明细</h3>
        {monthlyLoading ? (
          <LoadingSpinner />
        ) : (
          <SortableTable
            columns={monthlyColumns}
            data={monthlyData?.monthly_data ?? []}
            rowKey={(r) => r.month}
            defaultSortKey="month"
            defaultSortDir="asc"
            emptyMessage="暂无月度数据"
          />
        )}
      </section>

      <section>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">项目投入明细</h3>
        {projectsLoading ? (
          <LoadingSpinner />
        ) : (
          <SortableTable
            columns={projectColumns}
            data={projectsData ?? []}
            rowKey={(r) => r.project_name}
            defaultSortKey="person_days"
            defaultSortDir="desc"
            emptyMessage="暂无项目数据"
          />
        )}
      </section>
    </div>
  );
}
