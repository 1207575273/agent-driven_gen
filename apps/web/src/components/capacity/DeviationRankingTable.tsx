import { useCallback, useState } from "react";
import type { PersonDeviation } from "../../api/capacity";
import { useDeviationRanking } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

const DIRECTION_OPTIONS = [
  { value: "all", label: "全部" },
  { value: "negative", label: "负偏差" },
  { value: "positive", label: "正偏差" },
];

export function DeviationRankingTable() {
  const [direction, setDirection] = useState("all");
  const [abnormalOnly, setAbnormalOnly] = useState(false);
  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);
  const { timePeriod } = useFilterStore();

  const { data, isLoading, isError } = useDeviationRanking({
    deviationDirection: direction,
    sortBy: "deviation_abs",
    sortDir: "desc",
    isAbnormalOnly: abnormalOnly,
  });

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
      title: "应有",
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
      title: "实际",
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
      key: "is_abnormal",
      title: "状态",
      dataIndex: "is_abnormal",
      render: (v) =>
        v ? (
          <span className="inline-flex items-center rounded-full bg-red-900/30 px-2 py-0.5 text-xs text-red-400">
            异常
          </span>
        ) : (
          <span className="text-neutral-500">-</span>
        ),
    },
  ];

  if (isLoading) return <LoadingSpinner />;

  if (isError) {
    return (
      <div className="rounded-lg border border-red-900/50 bg-red-900/10 p-4 text-sm text-red-400">
        加载偏差数据失败
      </div>
    );
  }

  return (
    <div>
      {/* Filters */}
      <div className="flex items-center gap-3 mb-4">
        <div className="flex rounded-md border border-neutral-700 overflow-hidden">
          {DIRECTION_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => setDirection(opt.value)}
              className={`px-3 py-1 text-xs transition-colors ${
                direction === opt.value
                  ? "bg-accent/20 text-accent"
                  : "bg-neutral-900 text-neutral-500 hover:text-neutral-300"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 text-xs text-neutral-400">
          <input
            type="checkbox"
            checked={abnormalOnly}
            onChange={(e) => setAbnormalOnly(e.target.checked)}
            className="rounded border-neutral-700 bg-neutral-900 accent-accent"
          />
          仅显示异常
        </label>
      </div>

      <SortableTable
        columns={columns}
        data={data ?? []}
        rowKey={(r) => String(r.employee_id)}
        highlightRow={(r) => r.is_abnormal}
        highlightClass="bg-red-900/20"
        onRowClick={handleRowClick}
        emptyMessage="暂无比对数据"
        defaultSortKey="deviation"
        defaultSortDir="desc"
      />

      {drillPerson && (
        <DrillDownModal
          open={Boolean(drillPerson)}
          onClose={handleCloseModal}
          title={`偏差排行 > 人员: ${drillPerson.name}`}
          breadcrumbs={[{ label: drillPerson.name }]}
        >
          <PersonDetailContent
            employeeId={drillPerson.employeeId}
            employeeName={drillPerson.name}
            timePeriod={timePeriod ?? undefined}
          />
        </DrillDownModal>
      )}
    </div>
  );
}
