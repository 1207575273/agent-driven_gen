import { useCallback, useState } from "react";
import type { DepartmentFillRate } from "../../api/capacity";
import { useDepartmentFillRates } from "../../hooks/useCapacity";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";

export function DepartmentFillRateTable() {
  const [drillDept, setDrillDept] = useState<string | undefined>(undefined);
  const { data, isLoading, isError } = useDepartmentFillRates(drillDept);

  const handleDrill = useCallback((record: DepartmentFillRate) => {
    if (record.has_children) {
      setDrillDept(record.dept_path);
    }
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillDept(undefined);
  }, []);

  const columns: Column<DepartmentFillRate>[] = [
    { key: "dept_name", title: "部门", dataIndex: "dept_name", sortable: true },
    {
      key: "person_count",
      title: "人数",
      dataIndex: "person_count",
      sortable: true,
      align: "right",
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
      key: "actual_days",
      title: "实际产能",
      dataIndex: "actual_days",
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
      key: "fill_rate",
      title: "填报率",
      dataIndex: "fill_rate",
      sortable: true,
      align: "right",
      render: (value) => {
        const num = Number(value);
        const label = Number.isNaN(num) ? "-" : `${num.toFixed(1)}%`;
        return <span className={num < 80 ? "text-amber-400" : "text-accent"}>{label}</span>;
      },
    },
    {
      key: "abnormal_count",
      title: "异常人数",
      dataIndex: "abnormal_count",
      sortable: true,
      align: "right",
      render: (value) => {
        const num = Number(value);
        return num > 0 ? <span className="text-red-400">{num}</span> : <span>{num}</span>;
      },
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  if (isError) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载部门填报率数据失败
      </div>
    );
  }

  const tableData = data ?? [];

  return (
    <div>
      <SortableTable
        columns={columns}
        data={tableData}
        rowKey={(r) => r.dept_path}
        highlightRow={(r) => r.fill_rate < 80}
        highlightClass="bg-yellow-900/20"
        onRowClick={(r) => handleDrill(r)}
        emptyMessage="暂无部门数据"
        defaultSortKey="fill_rate"
        defaultSortDir="desc"
      />

      {drillDept && (
        <DrillDownModal
          open={Boolean(drillDept)}
          onClose={handleCloseModal}
          title={`部门下钻: ${drillDept}`}
          breadcrumbs={[{ label: drillDept, onClick: handleCloseModal }]}
          loading={isLoading}
        >
          <DepartmentFillRateTable />
        </DrillDownModal>
      )}
    </div>
  );
}
