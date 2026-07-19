import { useCallback, useState } from "react";
import type { CellPersonItem, DeptCategoryMatrix } from "../../api/capacity";
import { useCellPersons, useMatrix } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { Heatmap, type HeatmapCellClickPayload } from "../charts/Heatmap";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function MatrixPanel() {
  const { data, isLoading, isError } = useMatrix();
  const { timePeriod, deptLevel } = useFilterStore();

  // Drill state
  const [drillCell, setDrillCell] = useState<{
    deptName: string;
    categoryName: string;
    categoryId: number;
  } | null>(null);
  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);

  const { data: cellPersons, isLoading: cellLoading } = useCellPersons({
    timePeriod,
    categoryId: drillCell?.categoryId ?? null,
    deptLevel,
    deptName: drillCell?.deptName ?? null,
  });

  // ALL hooks and callbacks BEFORE early return
  const handleCellClick = useCallback((payload: HeatmapCellClickPayload) => {
    setDrillCell({
      deptName: payload.yLabel,
      categoryName: payload.xLabel,
      categoryId: payload.xIndex + 1,
    });
    setDrillPerson(null);
  }, []);

  const handlePersonClick = useCallback((record: CellPersonItem) => {
    setDrillPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillCell(null);
    setDrillPerson(null);
  }, []);

  const personColumns: Column<CellPersonItem>[] = [
    { key: "name", title: "姓名", dataIndex: "name" },
    { key: "dept_name", title: "部门", dataIndex: "dept_name" },
    { key: "role", title: "角色", dataIndex: "role" },
    {
      key: "category_days",
      title: "分类人天",
      dataIndex: "category_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "total_days",
      title: "总人天",
      dataIndex: "total_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    {
      key: "percentage",
      title: "占比",
      dataIndex: "percentage",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : `${num.toFixed(1)}%`;
      },
    },
  ];

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无综合交叉矩阵数据
      </div>
    );
  }

  const matrixData: DeptCategoryMatrix = data;

  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">部门x分类矩阵</h3>
      <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
        <Heatmap
          xLabels={matrixData.categories}
          yLabels={matrixData.depts}
          data={matrixData.matrix}
          height={Math.max(280, matrixData.depts.length * 50 + 80)}
          onCellClick={handleCellClick}
        />
      </div>

      {drillCell && (
        <DrillDownModal
          open={Boolean(drillCell)}
          onClose={handleCloseModal}
          title={
            drillPerson
              ? `综合交叉 > ${drillCell.deptName} × ${drillCell.categoryName} > 人员: ${drillPerson.name}`
              : `综合交叉 > ${drillCell.deptName} × ${drillCell.categoryName}`
          }
          breadcrumbs={
            drillPerson
              ? [
                  {
                    label: `${drillCell.deptName} × ${drillCell.categoryName}`,
                    onClick: () => setDrillPerson(null),
                  },
                  { label: drillPerson.name },
                ]
              : [{ label: `${drillCell.deptName} × ${drillCell.categoryName}` }]
          }
          loading={cellLoading}
        >
          {drillPerson ? (
            <PersonDetailContent
              employeeId={drillPerson.employeeId}
              employeeName={drillPerson.name}
              timePeriod={timePeriod ?? undefined}
            />
          ) : (
            <SortableTable
              columns={personColumns}
              data={cellPersons ?? []}
              rowKey={(r) => String(r.employee_id)}
              onRowClick={handlePersonClick}
              emptyMessage="暂无人员数据"
              defaultSortKey="category_days"
              defaultSortDir="desc"
            />
          )}
        </DrillDownModal>
      )}
    </div>
  );
}
