import type { RoleCategoryItem } from "../../api/capacity";
import { useRoleCategory } from "../../hooks/useCapacity";
import { BarChart } from "../charts/BarChart";
import { PieChart } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";

export function RoleCategoryPanel() {
  const { data, isLoading, isError } = useRoleCategory();

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

  const stackedSeries = categoryList.map((catName) => ({
    name: catName,
    data: items.map((d) => d.category_distribution[catName] ?? 0),
  }));

  // 人均产能柱状图
  const personAvgSeries = {
    name: "人均产能",
    data: items.map((d) => d.avg_days_per_person),
    color: "#38bdf8",
  };

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
          <BarChart categories={roleNames} series={stackedSeries} stacked height={340} />
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
      <RoleCategoryCrossTable data={items} />
    </div>
  );
}

function RoleCategoryCrossTable({ data }: { data: RoleCategoryItem[] }) {
  const allCategories = new Set<string>();
  for (const item of data) {
    for (const catName of Object.keys(item.category_distribution)) {
      allCategories.add(catName);
    }
  }
  const categoryList = [...allCategories];

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
                {categoryList.map((cat) => (
                  <td key={cat} className="px-3 py-2.5 text-sm text-neutral-300 text-right">
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
