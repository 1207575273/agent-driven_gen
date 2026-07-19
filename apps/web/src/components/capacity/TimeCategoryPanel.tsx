import { useCallback, useMemo, useState } from "react";
import type { CategoryProjectItem, DrillDownRecord, TimeCategoryItem } from "../../api/capacity";
import { useCategoryProjects, useDrillDownRecords, useTimeCategory } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart, type BarClickPayload } from "../charts/BarChart";
import { LineChart, type LineClickPayload } from "../charts/LineChart";
import { PieChart, type PieClickPayload } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function TimeCategoryPanel() {
  const { data, isLoading, isError } = useTimeCategory();
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();

  // Drill state: 2-level drill (category -> project -> person)
  const [drillState, setDrillState] = useState<{
    categoryName: string;
    categoryId: number;
    timeLabel?: string;
    projectName?: string | null;
    personId?: number | null;
    personName?: string | null;
  } | null>(null);

  const { data: categoryProjects, isLoading: projLoading } = useCategoryProjects({
    timePeriod,
    categoryId: drillState?.categoryId ?? null,
    deptLevel,
    deptName,
    role,
  });

  const { data: personRecords, isLoading: recLoading } = useDrillDownRecords(
    drillState?.projectName
      ? {
          project_name: drillState.projectName,
          time_period: timePeriod,
          limit: 100,
        }
      : {},
  );

  // Compute early (before useCallbacks)
  const items: TimeCategoryItem[] = (data ?? []) as TimeCategoryItem[];
  const firstItem = items[0];

  const catIdMap = useMemo(() => {
    const map: Record<string, number> = {};
    for (const c of firstItem?.categories || []) {
      if (c.category_id) map[c.category_name] = c.category_id;
    }
    return map;
  }, [firstItem]);

  const handleSliceClick = useCallback((payload: PieClickPayload) => {
    setDrillState({
      categoryName: payload.name,
      categoryId: Number((payload as unknown as Record<string, unknown>).category_id ?? 0),
    });
  }, []);

  const handleBarOrLineClick = useCallback(
    (payload: BarClickPayload | LineClickPayload, catIdxMap: Record<string, number>) => {
      const catId = catIdMap[payload.seriesName] ?? (catIdxMap[payload.seriesName] ?? 0) + 1;
      setDrillState({
        categoryName: payload.seriesName,
        categoryId: catId,
        timeLabel: payload.category,
      });
    },
    [catIdMap],
  );

  const handleProjectClick = useCallback((record: CategoryProjectItem) => {
    setDrillState((prev) =>
      prev ? { ...prev, projectName: record.project_name, personId: null, personName: null } : null,
    );
  }, []);

  const handlePersonClick = useCallback((record: DrillDownRecord) => {
    setDrillState((prev) =>
      prev ? { ...prev, personId: record.employee_id, personName: record.reporter } : null,
    );
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillState(null);
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无时间x分类数据
      </div>
    );
  }

  // pieData from nested categories -- embed category_id for drill
  const pieData = (firstItem?.categories || []).map((c) => ({
    name: c.category_name,
    value: c.total_days,
    category_id: c.category_id ?? 0,
  }));

  // time labels
  const timeLabels = items.map((d) => d.time_label);

  // category names across all items
  const allCatNames = [
    ...new Set(items.flatMap((d) => (d.categories || []).map((c) => c.category_name))),
  ];

  // stacked bar: each series is a category, each data point is total_days per time period
  const stackedSeries = allCatNames.map((catName) => ({
    name: catName,
    data: items.map((d) => {
      const match = (d.categories || []).find((c) => c.category_name === catName);
      return match ? match.total_days : 0;
    }),
  }));

  const trendSeries = allCatNames.map((catName) => ({
    name: catName,
    data: items.map((d) => {
      const match = (d.categories || []).find((c) => c.category_name === catName);
      return match ? match.total_days : 0;
    }),
  }));

  // Build category index map for id resolution
  const catIdxMap: Record<string, number> = {};
  allCatNames.forEach((cat, idx) => {
    catIdxMap[cat] = idx;
  });

  const projectColumns: Column<CategoryProjectItem>[] = [
    { key: "project_name", title: "项目名称", dataIndex: "project_name" },
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
    {
      key: "person_count",
      title: "人数",
      dataIndex: "person_count",
      align: "right",
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

  const recordColumns: Column<DrillDownRecord>[] = [
    { key: "reporter", title: "姓名", dataIndex: "reporter" },
    { key: "reporter_department", title: "部门", dataIndex: "reporter_department" },
    { key: "project_name", title: "项目", dataIndex: "project_name" },
    {
      key: "hours",
      title: "工时(h)",
      dataIndex: "hours",
      align: "right",
      render: (v) => {
        const num = Number(v);
        return Number.isNaN(num) ? "-" : num.toFixed(1);
      },
    },
    { key: "report_date", title: "日期", dataIndex: "report_date" },
  ];

  const breadcrumbs = [];
  if (drillState) {
    const catLabel = drillState.timeLabel
      ? `${drillState.categoryName} (${drillState.timeLabel})`
      : drillState.categoryName;
    breadcrumbs.push({
      label: catLabel,
      onClick: () =>
        setDrillState((prev) =>
          prev ? { ...prev, projectName: null, personId: null, personName: null } : null,
        ),
    });
    if (drillState.projectName) {
      breadcrumbs.push({
        label: drillState.projectName,
        onClick: () =>
          setDrillState((prev) => (prev ? { ...prev, personId: null, personName: null } : null)),
      });
    }
    if (drillState.personName) {
      breadcrumbs.push({ label: drillState.personName });
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">大类占比分布</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <PieChart
            data={pieData}
            height={320}
            innerRadius="50%"
            onSliceClick={(payload) => handleSliceClick(payload)}
          />
        </div>
      </div>

      {timeLabels.length > 1 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">各时段分类投入对比</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <BarChart
              categories={timeLabels}
              series={stackedSeries}
              stacked
              height={320}
              onBarClick={(payload) => handleBarOrLineClick(payload, catIdxMap)}
            />
          </div>
        </div>
      )}

      {timeLabels.length > 2 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">大类投入趋势</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <LineChart
              categories={timeLabels}
              series={trendSeries}
              height={300}
              onPointClick={(payload) => handleBarOrLineClick(payload, catIdxMap)}
            />
          </div>
        </div>
      )}

      {drillState && (
        <DrillDownModal
          open={Boolean(drillState)}
          onClose={handleCloseModal}
          title={
            drillState.personId
              ? `时间×分类 > ${drillState.categoryName} > ${drillState.projectName ?? ""} > 人员: ${drillState.personName ?? ""}`
              : drillState.projectName
                ? `时间×分类 > ${drillState.categoryName} > ${drillState.projectName}`
                : `时间×分类 > ${drillState.categoryName}`
          }
          breadcrumbs={breadcrumbs}
          loading={projLoading || recLoading}
        >
          {drillState.personId ? (
            <PersonDetailContent
              employeeId={drillState.personId}
              employeeName={drillState.personName ?? ""}
              timePeriod={timePeriod ?? undefined}
            />
          ) : drillState.projectName ? (
            <SortableTable
              columns={recordColumns}
              data={personRecords ?? []}
              rowKey={(r) => String(r.id)}
              onRowClick={handlePersonClick}
              emptyMessage="暂无人员工时"
              defaultSortKey="hours"
              defaultSortDir="desc"
            />
          ) : (
            <SortableTable
              columns={projectColumns}
              data={categoryProjects ?? []}
              rowKey={(r) => r.project_name}
              onRowClick={handleProjectClick}
              emptyMessage="该项目分类下暂无项目"
              defaultSortKey="person_days"
              defaultSortDir="desc"
            />
          )}
        </DrillDownModal>
      )}
    </div>
  );
}
