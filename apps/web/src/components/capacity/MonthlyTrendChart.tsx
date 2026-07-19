import { useCallback, useState } from "react";
import type { MonthlyPersonItem, MonthlyTrend } from "../../api/capacity";
import { useMonthlyPersons, useMonthlyTrend } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart, type BarClickPayload } from "../charts/BarChart";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function MonthlyTrendChart() {
  const { data, isLoading, isError } = useMonthlyTrend();
  const { deptLevel, deptName, role } = useFilterStore();

  // Drill state: month -> person
  const [drillMonth, setDrillMonth] = useState<string | null>(null);
  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);

  const { data: monthlyPersons, isLoading: personsLoading } = useMonthlyPersons({
    month: drillMonth,
    deptLevel,
    deptName,
    role,
  });

  const handleBarClick = useCallback((payload: BarClickPayload) => {
    // payload.category is like "1月" or "12月"
    // Map back to "2026-MM" format
    const monthMatch = payload.category.match(/^(\d+)月$/);
    if (monthMatch) {
      const m = (monthMatch[1] ?? "").padStart(2, "0");
      setDrillMonth(`2026-${m}`);
      setDrillPerson(null);
    }
  }, []);

  const handlePersonClick = useCallback((record: MonthlyPersonItem) => {
    setDrillPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillMonth(null);
    setDrillPerson(null);
  }, []);

  const personColumns: Column<MonthlyPersonItem>[] = [
    { key: "name", title: "姓名", dataIndex: "name" },
    { key: "dept_name", title: "部门", dataIndex: "dept_name" },
    { key: "role", title: "角色", dataIndex: "role" },
    {
      key: "actual_days",
      title: "实际人天",
      dataIndex: "actual_days",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-700 border-t-accent" />
      </div>
    );
  }

  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无月度趋势数据
      </div>
    );
  }

  const trendData: MonthlyTrend[] = data;

  const categories = trendData.map((item: MonthlyTrend) => {
    const parts = item.month.split("-");
    const monthNum = parts[1] ? Number.parseInt(parts[1], 10) : 0;
    return `${monthNum}月`;
  });

  const shouldSeries = trendData.map((item: MonthlyTrend) => item.should_be_days);
  const actualSeries = trendData.map((item: MonthlyTrend) => item.actual_days);
  const fillRateSeries = trendData.map((item: MonthlyTrend) => item.fill_rate);

  return (
    <>
      <BarChart
        categories={categories}
        series={[
          { name: "应有产能", data: shouldSeries, color: "#38bdf8" },
          { name: "实际产能", data: actualSeries, color: "#818cf8" },
          {
            name: "填报率(%)",
            data: fillRateSeries,
            type: "line",
            color: "#f97316",
            yAxisIndex: 1,
          },
        ]}
        height={320}
        onBarClick={handleBarClick}
      />

      {drillMonth && (
        <DrillDownModal
          open={Boolean(drillMonth)}
          onClose={handleCloseModal}
          title={
            drillPerson
              ? `月度趋势 > ${drillMonth} > 人员: ${drillPerson.name}`
              : `月度趋势 > ${drillMonth}`
          }
          breadcrumbs={
            drillPerson
              ? [
                  { label: drillMonth, onClick: () => setDrillPerson(null) },
                  { label: drillPerson.name },
                ]
              : [{ label: drillMonth }]
          }
          loading={personsLoading}
        >
          {drillPerson ? (
            <PersonDetailContent
              employeeId={drillPerson.employeeId}
              employeeName={drillPerson.name}
              timePeriod={drillMonth}
            />
          ) : (
            <SortableTable
              columns={personColumns}
              data={monthlyPersons ?? []}
              rowKey={(r) => String(r.employee_id)}
              onRowClick={handlePersonClick}
              emptyMessage="该月暂无人员数据"
              defaultSortKey="actual_days"
              defaultSortDir="desc"
            />
          )}
        </DrillDownModal>
      )}
    </>
  );
}
