import { useCallback, useEffect, useRef, useState } from "react";
import type {
  CategoryProjectItem,
  CellPersonItem,
  DeptCategoryItem,
  DrillDownRecord,
} from "../../api/capacity";
import {
  useCategoryProjects,
  useCellPersons,
  useDeptCategory,
  useDeptCategoryMatrix,
  useDrillDownRecords,
} from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart } from "../charts/BarChart";
import { Heatmap, type HeatmapCellClickPayload } from "../charts/Heatmap";
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

export function DeptCategoryPanel() {
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
      setDrillCell(null);
      setCellPerson(null);
      prevFilterRef.current = { timePeriod, deptLevel, deptName, role, categoryLevel: filterLevel };
    }
  });

  // 分层下钻: 起始层级由筛选器 categoryLevel 决定
  const [drillStack, setDrillStack] = useState<DrillLevel[]>([]);
  const currentDrill = drillStack.length > 0 ? drillStack[drillStack.length - 1] : null;
  const baseLevel = filterLevel;
  const currentLevel = currentDrill ? currentDrill.categoryLevel : baseLevel;
  const parentCategoryId = currentDrill ? currentDrill.categoryId : null;

  const { data, isLoading, isError } = useDeptCategory(currentLevel, parentCategoryId ?? undefined);
  const { data: matrixData, isLoading: matrixLoading } = useDeptCategoryMatrix();

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

  // Heatmap drill state
  const [drillCell, setDrillCell] = useState<{
    deptName: string;
    categoryName: string;
    categoryId: number;
  } | null>(null);
  const [cellPerson, setCellPerson] = useState<{ employeeId: number; name: string } | null>(null);

  const { data: cellPersons, isLoading: cellLoading } = useCellPersons({
    timePeriod,
    categoryId: drillCell?.categoryId ?? null,
    deptLevel,
    deptName: drillCell?.deptName ?? null,
  });

  const rawItems: DeptCategoryItem[] = data ?? [];
  const categoryIdMap: Record<string, number> = {};
  for (const item of rawItems) {
    if (item.category_ids) {
      for (const [catName, catId] of Object.entries(item.category_ids)) {
        categoryIdMap[catName] = catId;
      }
    }
  }

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

  const handleHeatmapClick = useCallback(
    (payload: HeatmapCellClickPayload) => {
      const catId = categoryIdMap[payload.xLabel] ?? payload.xIndex + 1;
      setDrillCell({ deptName: payload.yLabel, categoryName: payload.xLabel, categoryId: catId });
      setCellPerson(null);
    },
    [categoryIdMap],
  );

  const handleCellPersonClick = useCallback((record: CellPersonItem) => {
    setCellPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleProjectClick = useCallback((record: CategoryProjectItem) => {
    setDrillProject(record.project_name);
    setDrillPerson(null);
  }, []);

  const handlePersonClick = useCallback((record: DrillDownRecord) => {
    setDrillPerson({ employeeId: record.employee_id ?? 0, name: record.reporter });
  }, []);

  const handleDrillLevelPop = useCallback((idx: number) => {
    if (idx === -1) {
      setDrillStack([]);
    } else {
      setDrillStack((prev) => prev.slice(0, idx + 1));
    }
    setShowProjects(null);
    setDrillProject(null);
    setDrillPerson(null);
  }, []);

  const handleCloseModal = useCallback(() => {
    setShowProjects(null);
    setDrillProject(null);
    setDrillPerson(null);
    setDrillCell(null);
    setCellPerson(null);
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
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无部门x分类数据
      </div>
    );
  }

  const items: DeptCategoryItem[] = data;

  const allCategories = new Set<string>();
  for (const item of items) {
    for (const catName of Object.keys(item.category_distribution)) {
      allCategories.add(catName);
    }
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

  const deptNames = items.map((d: DeptCategoryItem) => d.dept_name);

  const stackedSeries = categoryList.map((catName: string) => ({
    name: catName,
    data: items.map((d: DeptCategoryItem) => d.category_distribution[catName] ?? 0),
  }));

  const breadcrumbs: { label: string; onClick: () => void }[] = [];
  if (drillStack.length > 0) {
    breadcrumbs.push({ label: "组织×分类", onClick: () => handleDrillLevelPop(-1) });
    for (let i = 0; i < drillStack.length; i++) {
      const lvl = drillStack[i];
      if (!lvl) continue;
      const cap = i === drillStack.length - 1;
      breadcrumbs.push({
        label: lvl.categoryName,
        onClick: cap ? () => {} : () => handleDrillLevelPop(i),
      });
    }
  }
  if (showProjects) {
    breadcrumbs.push({ label: showProjects.categoryName, onClick: () => {} });
    if (drillProject) {
      breadcrumbs.push({
        label: drillProject,
        onClick: drillPerson ? () => setDrillPerson(null) : () => {},
      });
      if (drillPerson) breadcrumbs.push({ label: drillPerson.name, onClick: () => {} });
    }
  }
  const showModal = Boolean(showProjects) || Boolean(drillCell);

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

      {pieData.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">
            {currentLevel === 1 ? "大类占比" : currentLevel === 2 ? "分类占比" : "细分占比"}
          </h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <PieChart
              data={pieData}
              height={320}
              innerRadius="50%"
              onSliceClick={handleSliceClick}
            />
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
      )}

      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">各部门分类投入分布</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <BarChart categories={deptNames} series={stackedSeries} stacked height={360} />
        </div>
      </div>

      {!matrixLoading && matrixData && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">部门x分类热力图</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <Heatmap
              xLabels={matrixData.categories}
              yLabels={matrixData.depts}
              data={matrixData.matrix}
              height={Math.max(280, matrixData.depts.length * 50 + 80)}
              onCellClick={handleHeatmapClick}
            />
          </div>
        </div>
      )}

      <DeptCategoryCrossTable
        data={items}
        categoryList={categoryList}
      />

      {showModal &&
        (() => {
          const activeModal = showProjects || drillCell;
          if (!activeModal) return null;
          const title = drillCell
            ? cellPerson
              ? `组织×分类 > ${drillCell.deptName} × ${drillCell.categoryName} > ${cellPerson.name}`
              : `组织×分类 > ${drillCell.deptName} × ${drillCell.categoryName}`
            : drillPerson
              ? `组织×分类 > ${activeModal.categoryName} > ${drillProject ?? ""} > ${drillPerson.name}`
              : drillProject
                ? `组织×分类 > ${activeModal.categoryName} > ${drillProject}`
                : `组织×分类 > ${activeModal.categoryName}`;
          return (
            <DrillDownModal
              open={showModal}
              onClose={handleCloseModal}
              title={title}
              breadcrumbs={
                drillCell
                  ? cellPerson
                    ? [
                        {
                          label: `${drillCell.deptName} × ${drillCell.categoryName}`,
                          onClick: () => setCellPerson(null),
                        },
                        { label: cellPerson.name },
                      ]
                    : [{ label: `${drillCell.deptName} × ${drillCell.categoryName}` }]
                  : breadcrumbs
              }
              loading={drillCell ? cellLoading : projLoading || recLoading}
            >
              {drillCell ? (
                cellPerson ? (
                  <PersonDetailContent
                    employeeId={cellPerson.employeeId}
                    employeeName={cellPerson.name}
                    timePeriod={timePeriod ?? undefined}
                  />
                ) : (
                  <SortableTable
                    columns={personColumns}
                    data={cellPersons ?? []}
                    rowKey={(r) => String(r.employee_id)}
                    onRowClick={handleCellPersonClick}
                    emptyMessage="暂无人员数据"
                    defaultSortKey="category_days"
                    defaultSortDir="desc"
                  />
                )
              ) : drillPerson ? (
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

function DeptCategoryCrossTable({
  data,
  categoryList,
}: {
  data: DeptCategoryItem[];
  categoryList: string[];
}) {
  const [showPct, setShowPct] = useState(false);

  const formatCell = (value: number, item: DeptCategoryItem) => {
    if (showPct) {
      return item.total_days > 0 ? `${((value / item.total_days) * 100).toFixed(1)}%` : "-";
    }
    return value.toFixed(1);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-neutral-400">部门x分类交叉表</h3>
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
                部门
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
              <tr key={item.dept_path} className="border-t border-neutral-800/50">
                <td className="px-3 py-2.5 text-sm text-neutral-200">{item.dept_name}</td>
                {categoryList.map((cat) => (
                  <td key={cat} className="px-3 py-2.5 text-sm text-neutral-300 text-right">
                    {formatCell(item.category_distribution[cat] ?? 0, item)}
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
              <td className="px-3 py-2.5 text-sm font-medium text-neutral-100">汇总</td>
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
