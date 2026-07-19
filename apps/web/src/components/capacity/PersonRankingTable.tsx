import type { PersonRankingItem } from "../../api/capacity";
import { usePersonRanking } from "../../hooks/useCapacity";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";

export function PersonRankingTableComponent() {
  const { data, isLoading, isError } = usePersonRanking({
    sortBy: "actual_days",
    sortDir: "desc",
  });

  const columns: Column<PersonRankingItem>[] = [
    { key: "name", title: "姓名", dataIndex: "name", sortable: true },
    { key: "dept_name", title: "部门", dataIndex: "dept_name", sortable: true },
    { key: "role", title: "角色", dataIndex: "role", sortable: true },
    {
      key: "actual_days",
      title: "实际人天",
      dataIndex: "actual_days",
      sortable: true,
      align: "right",
      render: (value) => {
        const num = Number(value);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "should_be_days",
      title: "应有产能",
      dataIndex: "should_be_days",
      sortable: true,
      align: "right",
      render: (value) => {
        const num = Number(value);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "deviation",
      title: "偏差",
      dataIndex: "deviation",
      sortable: true,
      align: "right",
      render: (value) => {
        const num = Number(value);
        const formatted = Number.isNaN(num) ? "-" : `${num >= 0 ? "+" : ""}${num.toFixed(1)}`;
        return <span className={num < 0 ? "text-red-400" : "text-emerald-400"}>{formatted}</span>;
      },
    },
    {
      key: "project_count",
      title: "项目数",
      dataIndex: "project_count",
      sortable: true,
      align: "right",
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  if (isError) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载人员排名数据失败
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">个人产能排名(按实际人天降序)</h3>
      <SortableTable
        columns={columns}
        data={data ?? []}
        rowKey={(r) => String(r.employee_id)}
        emptyMessage="暂无人员数据"
        defaultSortKey="actual_days"
        defaultSortDir="desc"
      />
    </div>
  );
}
