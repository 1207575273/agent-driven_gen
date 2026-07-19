import { useCallback, useState } from "react";
import type { PersonCategoryItem } from "../../api/capacity";
import { usePersonCategory } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";
import { BarChart } from "../charts/BarChart";
import { PieChart } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { DrillDownModal } from "./DrillDownModal";
import { PersonDetailContent } from "./PersonDetailContent";

export function PersonCategoryPanel() {
  const { data, isLoading, isError } = usePersonCategory();
  const timePeriod = useFilterStore((s) => s.timePeriod);
  const deptName = useFilterStore((s) => s.deptName);
  const role = useFilterStore((s) => s.role);

  const [drillPerson, setDrillPerson] = useState<{
    employeeId: number;
    name: string;
  } | null>(null);

  const handlePersonClick = useCallback((record: PersonCategoryItem) => {
    setDrillPerson({ employeeId: record.employee_id, name: record.name });
  }, []);

  const handleCloseModal = useCallback(() => {
    setDrillPerson(null);
  }, []);

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无人员x分类数据
      </div>
    );
  }

  const items: PersonCategoryItem[] = data;

  // 提取所有类别
  const allCategories = new Set<string>();
  for (const item of items) {
    for (const catName of Object.keys(item.category_distribution)) {
      allCategories.add(catName);
    }
  }
  const categoryList = [...allCategories];

  // 饼图: 全量人员汇总到分类
  const pieMap: Record<string, number> = {};
  for (const item of items) {
    for (const [cat, days] of Object.entries(item.category_distribution)) {
      pieMap[cat] = (pieMap[cat] || 0) + days;
    }
  }
  const pieData = Object.entries(pieMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  // 堆叠柱状图: Top 30 人员在各分类上的投入
  const barMax = 30;
  const topItems = items.slice(0, barMax);
  const personLabels = topItems.map((d) => d.name);

  const stackedSeries = categoryList.map((catName) => ({
    name: catName,
    data: topItems.map((d) => d.category_distribution[catName] ?? 0),
  }));

  return (
    <div className="space-y-6">
      {/* 饼图: 分类产能占比 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">
          分类产能占比分布{deptName ? ` - ${deptName}` : ""}
          {role ? ` (${role})` : ""}
        </h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <PieChart data={pieData} height={320} innerRadius="50%" />
        </div>
      </div>

      {/* 堆叠柱状图: 各人员分类投入分布 (Top 30) */}
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

      {/* 人员x分类交叉表 */}
      <PersonCategoryCrossTable
        data={items}
        categoryList={categoryList}
        onPersonClick={handlePersonClick}
      />

      {drillPerson && (
        <DrillDownModal
          open={Boolean(drillPerson)}
          onClose={handleCloseModal}
          title={`人员维度 > ${drillPerson.name}`}
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

function PersonCategoryCrossTable({
  data,
  categoryList,
  onPersonClick,
}: {
  data: PersonCategoryItem[];
  categoryList: string[];
  onPersonClick: (record: PersonCategoryItem) => void;
}) {
  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">人员x分类交叉表</h3>
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
                      ? (item.category_distribution[cat] ?? 0).toFixed(1)
                      : "-"}
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
