import { useCallback, useState } from "react";
import type { PersonDeviation } from "../../api/capacity";
import { useAbnormalDetail } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function AbnormalDetailList() {
  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);
  const { timePeriod } = useFilterStore();
  const { data, isLoading, isError } = useAbnormalDetail();

  const handleRowClick = useCallback((record: PersonDeviation) => {
    setDrillPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillPerson(null);
  }, []);

  const columns: Column<PersonDeviation>[] = [
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
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "actual_days",
      title: "实际产能",
      dataIndex: "actual_days",
      sortable: true,
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
      sortable: true,
      align: "right",
      render: (v) => {
        const num = Number(v);
        const formatted = Number.isNaN(num) ? "-" : `${num >= 0 ? "+" : ""}${num.toFixed(1)}`;
        return <span className={num < 0 ? "text-red-400" : "text-emerald-400"}>{formatted}</span>;
      },
    },
    {
      key: "deviation_rate",
      title: "偏差率",
      dataIndex: "deviation_rate",
      sortable: true,
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : `${num.toFixed(1)}%`;
      },
    },
    {
      key: "project_count",
      title: "项目数",
      dataIndex: "project_count",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) || num === 0 ? "-" : String(num);
      },
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  if (isError) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载异常人员数据失败
      </div>
    );
  }

  return (
    <>
      <SortableTable
        columns={columns}
        data={data ?? []}
        rowKey={(r) => String(r.employee_id)}
        highlightRow={(r) => r.is_abnormal}
        highlightClass="bg-red-900/20"
        onRowClick={handleRowClick}
        emptyMessage="暂无异常人员"
        defaultSortKey="deviation"
        defaultSortDir="desc"
      />

      {drillPerson && (
        <DrillDownModal
          open={Boolean(drillPerson)}
          onClose={handleCloseModal}
          title={`异常明细 > 人员: ${drillPerson.name}`}
          breadcrumbs={[{ label: drillPerson.name }]}
        >
          <PersonDetailContent
            employeeId={drillPerson.employeeId}
            employeeName={drillPerson.name}
            timePeriod={timePeriod ?? undefined}
          />
        </DrillDownModal>
      )}
    </>
  );
}
