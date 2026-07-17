import type { RoleAggregationItem } from "../../api/capacity";

interface RoleAggregationTableProps {
  data: RoleAggregationItem[] | undefined;
  loading: boolean;
}

export function RoleAggregationTable({ data, loading }: RoleAggregationTableProps) {
  if (loading) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-neutral-600">
        加载中...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-neutral-600">
        暂无角色数据
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-800">
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">角色</th>
            <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">总人天</th>
            <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">人数</th>
            <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">人均人天</th>
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">部门分布</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.role} className="border-b border-neutral-900">
              <td className="px-4 py-3 text-sm text-neutral-100">{item.role}</td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.total_days.toLocaleString()}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.person_count}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.person_count > 0 ? (item.total_days / item.person_count).toFixed(1) : "—"}
              </td>
              <td className="px-4 py-3 text-sm text-neutral-500">
                {item.dept_distribution
                  .map((d) => `${d.department}(${d.person_count}人)`)
                  .join(", ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
