import type { ZeroFillingPerson } from "../../api/capacity";
import { useZeroFillingList } from "../../hooks/useCapacity";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";

export function ZeroFillingList() {
  const { data, isLoading, isError } = useZeroFillingList();

  const columns: Column<ZeroFillingPerson>[] = [
    { key: "name", title: "姓名", dataIndex: "name", sortable: true },
    { key: "dept_name", title: "部门", dataIndex: "dept_name", sortable: true },
    { key: "role", title: "角色", dataIndex: "role", sortable: true },
    {
      key: "should_be_days",
      title: "应有产能",
      dataIndex: "should_be_days",
      sortable: true,
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : `${num.toFixed(1)} 人天`;
      },
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  if (isError) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载零填报数据失败
      </div>
    );
  }

  return (
    <SortableTable
      columns={columns}
      data={data ?? []}
      rowKey={(r) => String(r.employee_id)}
      emptyMessage="暂无零填报人员"
      defaultSortKey="should_be_days"
      defaultSortDir="desc"
    />
  );
}
