import { useCallback, useState } from "react";
import type { ZeroFillingPerson } from "../../api/capacity";
import { useZeroFillingList } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function ZeroFillingList() {
  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);
  const { timePeriod } = useFilterStore();
  const { data, isLoading, isError } = useZeroFillingList();

  const handleRowClick = useCallback((record: ZeroFillingPerson) => {
    setDrillPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillPerson(null);
  }, []);

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
    <>
      <SortableTable
        columns={columns}
        data={data ?? []}
        rowKey={(r) => String(r.employee_id)}
        onRowClick={handleRowClick}
        emptyMessage="暂无零填报人员"
        defaultSortKey="should_be_days"
        defaultSortDir="desc"
      />

      {drillPerson && (
        <DrillDownModal
          open={Boolean(drillPerson)}
          onClose={handleCloseModal}
          title={`零填报 > 人员: ${drillPerson.name}`}
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
