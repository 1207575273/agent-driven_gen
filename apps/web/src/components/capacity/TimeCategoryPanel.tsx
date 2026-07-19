import type { TimeCategoryItem } from "../../api/capacity";
import { useTimeCategory } from "../../hooks/useCapacity";
import { BarChart } from "../charts/BarChart";
import { LineChart } from "../charts/LineChart";
import { PieChart } from "../charts/PieChart";
import { LoadingSpinner } from "../shared/LoadingSpinner";

export function TimeCategoryPanel() {
  const { data, isLoading, isError } = useTimeCategory();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data || data.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无时间x分类数据
      </div>
    );
  }

  // API returns array of {time_label, person_days, categories: [{category_name, total_days, percentage}]}
  const items: TimeCategoryItem[] = data;
  const firstItem = items[0];

  // pieData from nested categories
  const pieData = (firstItem?.categories || []).map((c) => ({
    name: c.category_name,
    value: c.total_days,
  }));

  // time labels
  const timeLabels = items.map((d) => d.time_label);

  // category names across all items
  const allCatNames = [
    ...new Set(items.flatMap((d) => (d.categories || []).map((c) => c.category_name))),
  ];

  // 堆叠柱状图: each series is a category, each data point is total_days per time period
  const stackedSeries = allCatNames.map((catName) => ({
    name: catName,
    data: items.map((d) => {
      const match = (d.categories || []).find((c) => c.category_name === catName);
      return match ? match.total_days : 0;
    }),
  }));

  // 趋势折线图
  const trendSeries = allCatNames.map((catName) => ({
    name: catName,
    data: items.map((d) => {
      const match = (d.categories || []).find((c) => c.category_name === catName);
      return match ? match.total_days : 0;
    }),
  }));

  return (
    <div className="space-y-6">
      {/* 饼图 */}
      <div>
        <h3 className="text-sm font-medium text-neutral-400 mb-3">大类占比分布</h3>
        <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
          <PieChart data={pieData} height={320} innerRadius="50%" />
        </div>
      </div>

      {/* 堆叠柱状图 */}
      {timeLabels.length > 1 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">各时段分类投入对比</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <BarChart categories={timeLabels} series={stackedSeries} stacked height={320} />
          </div>
        </div>
      )}

      {/* 趋势折线图 */}
      {timeLabels.length > 2 && (
        <div>
          <h3 className="text-sm font-medium text-neutral-400 mb-3">大类投入趋势</h3>
          <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
            <LineChart categories={timeLabels} series={trendSeries} height={300} />
          </div>
        </div>
      )}
    </div>
  );
}
