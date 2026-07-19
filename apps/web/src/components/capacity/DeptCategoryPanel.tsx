import type { DeptCategoryItem } from "../../api/capacity";
import { useDeptCategory, useDeptCategoryMatrix } from "../../hooks/useCapacity";
import { BarChart } from "../charts/BarChart";
import { Heatmap } from "../charts/Heatmap";
import { PieChart } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";

export function DeptCategoryPanel() {
  const { data, isLoading, isError } = useDeptCategory();
  const { data: matrixData, isLoading: matrixLoading } = useDeptCategoryMatrix();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无部门x分类数据
      </div>
    );
  }

  const items: DeptCategoryItem[] = data;

  // 提取所有类别名称
  const allCategories = new Set<string>();
  for (const item of items) {
    for (const catName of Object.keys(item.category_distribution)) {
      allCategories.add(catName);
    }
  }
  const categoryList = [...allCategories];

  // 饼图: 全部门按分类汇总
  const pieMap: Record<string, number> = {};
  for (const item of items) {
    for (const [cat, days] of Object.entries(item.category_distribution)) {
      pieMap[cat] = (pieMap[cat] || 0) + days;
    }
  }
  const pieData = Object.entries(pieMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const deptNames = items.map((d: DeptCategoryItem) => d.dept_name);

  const stackedSeries = categoryList.map((catName: string) => ({
    name: catName,
    data: items.map((d: DeptCategoryItem) => d.category_distribution[catName] ?? 0),
  }));

  return (
    <div className="space-y-6">
      {/* 饼图: 全量分类占比 */}
      {pieData.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">分类产能占比分布</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <PieChart data={pieData} height={320} innerRadius="50%" />
          </div>
        </div>
      )}

      {/* 堆叠柱状图: 各部门分类投入 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">各部门分类投入分布</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <BarChart categories={deptNames} series={stackedSeries} stacked height={360} />
        </div>
      </div>

      {/* 热力图矩阵 */}
      {!matrixLoading && matrixData && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">部门x分类热力图</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <Heatmap
              xLabels={matrixData.categories}
              yLabels={matrixData.depts}
              data={matrixData.matrix}
              height={Math.max(280, matrixData.depts.length * 50 + 80)}
            />
          </div>
        </div>
      )}

      {/* 填报率对比表 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">部门填报率与人均产能</h3>
        <div className="rounded-lg border border-neutral-800/50 overflow-hidden">
          <table className="min-w-full">
            <thead>
              <tr className="bg-neutral-900/50">
                <th className="px-3 py-3 text-left text-xs font-medium text-neutral-400 uppercase">
                  部门
                </th>
                <th className="px-3 py-3 text-right text-xs font-medium text-neutral-400 uppercase">
                  总人天
                </th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.dept_path} className="border-t border-neutral-800/50">
                  <td className="px-3 py-2.5 text-sm text-neutral-200">{item.dept_name}</td>
                  <td className="px-3 py-2.5 text-sm text-neutral-200 text-right">
                    {item.total_days.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
