import { useCallback, useState } from "react";
import type { CellPersonItem, RoleCategoryItem } from "../../api/capacity";
import { useCellPersons, useRoleCategory } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart, type BarClickPayload } from "../charts/BarChart";
import { PieChart } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { type Column, SortableTable } from "../shared/SortableTable";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function RoleCategoryPanel() {
  const { data, isLoading, isError } = useRoleCategory();
  const { timePeriod } = useFilterStore();

  // Drill state
  const [drillCell, setDrillCell] = useState<{
    role: string;
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
    role: drillCell?.role ?? null,
  });

  const handleBarClick = useCallback((payload: BarClickPayload) => {
    const catId =
      categoryIdMap[payload.seriesName] ?? (categoryIdxMap[payload.seriesName] ?? 0) + 1;
    setDrillCell({
      role: payload.category,
      categoryName: payload.seriesName,
      categoryId: catId,
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

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无角色x分类数据
      </div>
    );
  }

  const items: RoleCategoryItem[] = data;

  // 提取所有类别
  const allCategories = new Set<string>();
  for (const item of items) {
    for (const catName of Object.keys(item.category_distribution)) {
      allCategories.add(catName);
    }
  }
  const categoryList = [...allCategories];

  // 饼图: 全部角色按分类汇总
  const pieMap: Record<string, number> = {};
  for (const item of items) {
    for (const [cat, days] of Object.entries(item.category_distribution)) {
      pieMap[cat] = (pieMap[cat] || 0) + days;
    }
  }
  const pieData = Object.entries(pieMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const roleNames = items.map((d) => d.role);

  // Build a mapping from category name to id from API data
  const categoryIdMap: Record<string, number> = {};
  for (const item of items) {
    if (item.category_ids) {
      for (const [catName, catId] of Object.entries(item.category_ids)) {
        categoryIdMap[catName] = catId;
      }
    }
  }

  const stackedSeries = categoryList.map((catName) => ({
    name: catName,
    data: items.map((d) => d.category_distribution[catName] ?? 0),
  }));

  // Build a mapping from category name to index for id resolution in drill
  const categoryIdxMap: Record<string, number> = {};
  categoryList.forEach((cat, idx) => {
    categoryIdxMap[cat] = idx;
  });

  // 人均产能柱状图
  const personAvgSeries = {
    name: "人均产能",
    data: items.map((d) => d.avg_days_per_person),
    color: "#38bdf8",
  };

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

  return (
    <div className="space-y-6">
      {/* 饼图: 分类产能占比 */}
      {pieData.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">分类产能占比分布</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <PieChart data={pieData} height={320} innerRadius="50%" />
          </div>
        </div>
      )}

      {/* 堆叠柱状图 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">各角色分类投入分布</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <BarChart
            categories={roleNames}
            series={stackedSeries}
            stacked
            height={340}
            onBarClick={handleBarClick}
          />
        </div>
      </div>

      {/* 人均产能柱状图 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">各角色人均产能</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <BarChart categories={roleNames} series={[personAvgSeries]} height={280} />
        </div>
      </div>

      {/* 交叉表 */}
      <RoleCategoryCrossTable
        data={items}
        categoryList={categoryList}
        onCellClick={(role, categoryName, catIdx) => {
          const catId = categoryIdMap[categoryName] ?? catIdx + 1;
          setDrillCell({ role, categoryName, categoryId: catId });
          setDrillPerson(null);
        }}
      />

      {drillCell && (
        <DrillDownModal
          open={Boolean(drillCell)}
          onClose={handleCloseModal}
          title={
            drillPerson
              ? `角色×分类 > ${drillCell.role} × ${drillCell.categoryName} > 人员: ${drillPerson.name}`
              : `角色×分类 > ${drillCell.role} × ${drillCell.categoryName}`
          }
          breadcrumbs={
            drillPerson
              ? [
                  {
                    label: `${drillCell.role} × ${drillCell.categoryName}`,
                    onClick: () => setDrillPerson(null),
                  },
                  { label: drillPerson.name },
                ]
              : [{ label: `${drillCell.role} × ${drillCell.categoryName}` }]
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

function RoleCategoryCrossTable({
  data,
  categoryList,
  onCellClick,
}: {
  data: RoleCategoryItem[];
  categoryList: string[];
  onCellClick: (role: string, categoryName: string, catIdx: number) => void;
}) {
  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">角色x分类交叉表</h3>
      <div className="rounded-lg border border-neutral-800/50 overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-neutral-900/50">
              <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                角色
              </th>
              <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                人数
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
              <tr key={item.role} className="border-t border-neutral-800/50">
                <td className="px-3 py-2.5 text-sm text-neutral-200">{item.role}</td>
                <td className="px-3 py-2.5 text-sm text-neutral-200 text-right">
                  {item.person_count}
                </td>
                {categoryList.map((cat, catIdx) => (
                  <td
                    key={cat}
                    className="px-3 py-2.5 text-sm text-neutral-300 text-right cursor-pointer hover:bg-neutral-700/30 transition-colors"
                    onClick={() => onCellClick(item.role, cat, catIdx)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") onCellClick(item.role, cat, catIdx);
                    }}
                  >
                    {(item.category_distribution[cat] ?? 0).toFixed(1)}
                  </td>
                ))}
                <td className="px-3 py-2.5 text-sm text-neutral-100 text-right font-medium">
                  {item.total_days.toFixed(1)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
