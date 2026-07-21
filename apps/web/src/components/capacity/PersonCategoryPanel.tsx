import { useCallback, useEffect, useRef, useState } from "react";
import type { CategoryProjectItem, DrillDownRecord, PersonCategoryItem } from "../../api/capacity";
import {
  useCategoryProjects,
  useDrillDownRecords,
  usePersonCategory,
} from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart } from "../charts/BarChart";
import { PieChart, type PieClickPayload } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

interface DrillLevel {
  categoryName: string;
  categoryId: number;
  categoryLevel: number;
  parentCategoryId: number | null;
}

export function PersonCategoryPanel() {
  const { timePeriod, deptLevel, deptName, role, categoryLevel: filterLevel } = useFilterStore();

  // 筛选条件变化时自动重置下钻状态到筛选层级
  const prevFilterRef = useRef({
    timePeriod,
    deptLevel,
    deptName,
    role,
    categoryLevel: filterLevel,
  });
  useEffect(() => {
    const prev = prevFilterRef.current;
    if (
      prev.timePeriod !== timePeriod ||
      prev.deptLevel !== deptLevel ||
      prev.deptName !== deptName ||
      prev.role !== role ||
      prev.categoryLevel !== filterLevel
    ) {
      setDrillStack([]);
      setShowProjects(null);
      setDrillProject(null);
      setDrillPerson(null);
      setTablePerson(null);
      prevFilterRef.current = { timePeriod, deptLevel, deptName, role, categoryLevel: filterLevel };
    }
  });

  // 分层下钻: 起始层级由筛选器 categoryLevel 决定
  const [drillStack, setDrillStack] = useState<DrillLevel[]>([]);
  const currentDrill = drillStack.length > 0 ? drillStack[drillStack.length - 1] : null;
  const baseLevel = filterLevel;
  const currentLevel = currentDrill ? currentDrill.categoryLevel : baseLevel;
  const parentCategoryId = currentDrill ? currentDrill.categoryId : null;

  const { data, isLoading, isError } = usePersonCategory(
    currentLevel,
    parentCategoryId ?? undefined,
  );

  // 末级项目/人员弹窗
  const [showProjects, setShowProjects] = useState<{
    categoryId: number;
    categoryName: string;
  } | null>(null);
  const [drillProject, setDrillProject] = useState<string | null>(null);
  const [drillPerson, setDrillPerson] = useState<{ employeeId: number; name: string } | null>(null);

  const { data: categoryProjects, isLoading: projLoading } = useCategoryProjects({
    timePeriod,
    categoryId: showProjects?.categoryId ?? null,
    deptLevel,
    deptName,
    role,
  });

  const { data: personRecords, isLoading: recLoading } = useDrillDownRecords(
    drillProject ? { project_name: drillProject, time_period: timePeriod, limit: 100 } : {},
  );

  // Table row click → person detail
  const [tablePerson, setTablePerson] = useState<{ employeeId: number; name: string } | null>(null);

  const handleSliceClick = useCallback(
    (payload: PieClickPayload) => {
      const catId = payload.category_id ?? 0;
      if (currentLevel >= 3) {
        setShowProjects({ categoryId: catId, categoryName: payload.name });
        setDrillProject(null);
        setDrillPerson(null);
      } else {
        setDrillStack((prev) =>
          prev.concat({
            categoryName: payload.name,
            categoryId: catId,
            categoryLevel: currentLevel + 1,
            parentCategoryId: parentCategoryId,
          }),
        );
        setShowProjects(null);
        setDrillProject(null);
        setDrillPerson(null);
      }
    },
    [currentLevel, parentCategoryId],
  );

  const handleTableRowClick = useCallback((record: PersonCategoryItem) => {
    setTablePerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleProjectClick = useCallback((record: CategoryProjectItem) => {
    setDrillProject(record.project_name);
    setDrillPerson(null);
  }, []);

  const handlePersonClick = useCallback((record: DrillDownRecord) => {
    setDrillPerson({ employeeId: record.employee_id ?? 0, name: record.reporter });
  }, []);

  const handleDrillLevelPop = useCallback((idx: number) => {
    if (idx === -1) setDrillStack([]);
    else setDrillStack((prev) => prev.slice(0, idx + 1));
    setShowProjects(null);
    setDrillProject(null);
    setDrillPerson(null);
  }, []);

  const handleCloseModal = useCallback(() => {
    setShowProjects(null);
    setDrillProject(null);
    setDrillPerson(null);
    setTablePerson(null);
  }, []);

  const projColumns: Column<CategoryProjectItem>[] = [
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
    { key: "person_count", title: "人数", dataIndex: "person_count", align: "right" },
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

  const drillRecordColumns: Column<DrillDownRecord>[] = [
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

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无人员x分类数据
      </div>
    );
  }

  const items: PersonCategoryItem[] = data;

  const allCategories = new Set<string>();
  const categoryIdMap: Record<string, number> = {};
  for (const item of items) {
    if (item.category_ids) {
      for (const [catName, catId] of Object.entries(item.category_ids))
        categoryIdMap[catName] = catId;
    }
    for (const catName of Object.keys(item.category_distribution)) allCategories.add(catName);
  }
  const categoryList = [...allCategories];

  const pieMap: Record<string, number> = {};
  for (const item of items) {
    for (const [cat, days] of Object.entries(item.category_distribution)) {
      pieMap[cat] = (pieMap[cat] || 0) + days;
    }
  }
  const pieData = Object.entries(pieMap)
    .map(([name, value]) => ({ name, value, category_id: categoryIdMap[name] ?? 0 }))
    .sort((a, b) => b.value - a.value);

  const barMax = 30;
  const topItems = items.slice(0, barMax);
  const personLabels = topItems.map((d) => d.name);
  const stackedSeries = categoryList.map((catName) => ({
    name: catName,
    data: topItems.map((d) => d.category_distribution[catName] ?? 0),
  }));

  const showModal = Boolean(showProjects) || Boolean(tablePerson);

  return (
    <div className="space-y-6">
      {drillStack.length > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-neutral-500">下钻:</span>
          {drillStack.map((lvl, i) => (
            <span key={lvl.categoryId} className="flex items-center gap-1">
              {i > 0 && <span className="text-neutral-600">→</span>}
              <button
                type="button"
                onClick={() => handleDrillLevelPop(i)}
                className="text-accent hover:underline transition-colors"
              >
                {lvl.categoryName}
              </button>
            </span>
          ))}
          <button
            type="button"
            onClick={() => handleDrillLevelPop(-1)}
            className="text-xs text-neutral-500 hover:text-neutral-300 transition-colors ml-2"
          >
            ← 返回顶层
          </button>
        </div>
      )}

      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">
          {currentLevel === 1 ? "大类占比" : currentLevel === 2 ? "分类占比" : "细分占比"}
          {deptName ? ` - ${deptName}` : ""}
          {role ? ` (${role})` : ""}
        </h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <PieChart data={pieData} height={320} innerRadius="50%" onSliceClick={handleSliceClick} />
        </div>
        {currentLevel < 3 ? (
          <p className="text-xs text-neutral-500 mt-1 text-center">
            点击扇区可下钻到{currentLevel === 1 ? "分类" : "细分"}层级
          </p>
        ) : (
          <p className="text-xs text-neutral-500 mt-1 text-center">
            点击扇区查看分类下的项目列表 → 人员工时明细
          </p>
        )}
      </div>

      {personLabels.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">
            各人员分类投入分布（Top {personLabels.length}）
          </h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <BarChart categories={personLabels} series={stackedSeries} stacked height={420} />
          </div>
        </div>
      )}

      <PersonCategoryCrossTable
        data={items}
        categoryList={categoryList}
        onPersonClick={handleTableRowClick}
      />

      {showModal &&
        (() => {
          if (tablePerson) {
            return (
              <DrillDownModal
                open={Boolean(tablePerson)}
                onClose={handleCloseModal}
                title={`人员维度 > ${tablePerson.name}`}
                breadcrumbs={[{ label: tablePerson.name }]}
              >
                <PersonDetailContent
                  employeeId={tablePerson.employeeId}
                  employeeName={tablePerson.name}
                  timePeriod={timePeriod ?? undefined}
                />
              </DrillDownModal>
            );
          }
          if (!showProjects) return null;
          const sp = showProjects;
          return (
            <DrillDownModal
              open={showModal}
              onClose={handleCloseModal}
              title={
                drillPerson
                  ? `人员维度 > ${sp.categoryName} > ${drillProject ?? ""} > ${drillPerson.name}`
                  : drillProject
                    ? `人员维度 > ${sp.categoryName} > ${drillProject}`
                    : `人员维度 > ${sp.categoryName}`
              }
              breadcrumbs={
                drillPerson
                  ? [
                      {
                        label: `${sp.categoryName} > ${drillProject ?? ""}`,
                        onClick: () => setDrillPerson(null),
                      },
                      { label: drillPerson.name },
                    ]
                  : drillProject
                    ? [
                        { label: sp.categoryName, onClick: () => setDrillProject(null) },
                        { label: drillProject },
                      ]
                    : [{ label: sp.categoryName }]
              }
              loading={projLoading || recLoading}
            >
              {drillPerson ? (
                <PersonDetailContent
                  employeeId={drillPerson.employeeId}
                  employeeName={drillPerson.name}
                  timePeriod={timePeriod ?? undefined}
                />
              ) : drillProject ? (
                <SortableTable
                  columns={drillRecordColumns}
                  data={personRecords ?? []}
                  rowKey={(r) => String(r.id)}
                  onRowClick={handlePersonClick}
                  emptyMessage="暂无人员工时"
                  defaultSortKey="hours"
                  defaultSortDir="desc"
                />
              ) : (
                <SortableTable
                  columns={projColumns}
                  data={categoryProjects ?? []}
                  rowKey={(r) => r.project_name}
                  onRowClick={handleProjectClick}
                  emptyMessage="该项目分类下暂无项目"
                  defaultSortKey="person_days"
                  defaultSortDir="desc"
                />
              )}
            </DrillDownModal>
          );
        })()}
    </div>
  );
}

function PersonCategoryCrossTable({
  data,
  categoryList,
  onPersonClick,
}: {
  data: PersonCategoryItem[];
  categoryList: string[];
  onPersonClick: (record: PersonCategoryItem) => void;
}) {
  const [showPct, setShowPct] = useState(false);

  const formatCell = (value: number, item: PersonCategoryItem) => {
    if (showPct) {
      return item.total_days > 0 ? `${((value / item.total_days) * 100).toFixed(1)}%` : "-";
    }
    return value !== undefined ? value.toFixed(1) : "-";
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-neutral-400">人员x分类交叉表</h3>
        <div className="flex items-center gap-2 text-xs text-neutral-400 cursor-pointer select-none">
          <span className={!showPct ? "text-accent" : ""}>人天</span>
          <button
            type="button"
            onClick={() => setShowPct(!showPct)}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
              showPct ? "bg-accent/30" : "bg-neutral-700"
            }`}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
                showPct ? "translate-x-4" : "translate-x-1"
              }`}
            />
          </button>
          <span className={showPct ? "text-accent" : ""}>占比</span>
        </div>
      </div>
      <div className="rounded-lg border border-neutral-800/50 overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-neutral-900/50">
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                姓名
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                部门
              </th>
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                角色
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                项目数
              </th>
              {categoryList.map((cat) => (
                <th
                  key={cat}
                  className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase"
                >
                  {cat}
                </th>
              ))}
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                合计
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr
                key={item.employee_id}
                onClick={() => onPersonClick(item)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") onPersonClick(item);
                }}
                className="border-t border-neutral-800/50 hover:bg-neutral-800/20 transition-colors cursor-pointer"
              >
                <td className="px-3 py-2.5 text-sm text-neutral-200 whitespace-nowrap">
                  {item.name}
                </td>
                <td className="px-3 py-2.5 text-sm text-neutral-400 whitespace-nowrap max-w-[120px] truncate">
                  {item.dept_name}
                </td>
                <td className="px-3 py-2.5 text-sm text-neutral-400 whitespace-nowrap">
                  {item.role}
                </td>
                <td className="px-3 py-2.5 text-sm text-neutral-300 text-right">
                  {item.project_count}
                </td>
                {categoryList.map((cat) => (
                  <td key={cat} className="px-3 py-2.5 text-sm text-neutral-300 text-right">
                    {item.category_distribution[cat] !== undefined
                      ? formatCell(item.category_distribution[cat] ?? 0, item)
                      : "-"}
                  </td>
                ))}
                <td className="px-3 py-2.5 text-sm text-neutral-100 text-right font-medium">
                  {showPct ? "100%" : item.total_days.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-neutral-600 bg-neutral-900/60">
              <td className="px-3 py-2.5 text-sm font-medium text-neutral-100" colSpan={4}>
                汇总
              </td>
              {categoryList.map((cat) => {
                const sum = data.reduce((acc, item) => acc + (item.category_distribution[cat] ?? 0), 0);
                return (
                  <td key={cat} className="px-3 py-2.5 text-sm font-medium text-accent text-right">
                    {showPct
                      ? (() => {
                          const colSum = data.reduce((acc, item) => acc + (item.category_distribution[cat] ?? 0), 0);
                          const totalAll = data.reduce((acc, item) => acc + item.total_days, 0);
                          return totalAll > 0 ? `${((colSum / totalAll) * 100).toFixed(1)}%` : "-";
                        })()
                      : sum.toFixed(1)}
                  </td>
                );
              })}
              <td className="px-3 py-2.5 text-sm font-medium text-accent text-right">
                {showPct
                  ? "100%"
                  : data.reduce((acc, item) => acc + item.total_days, 0).toFixed(1)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
