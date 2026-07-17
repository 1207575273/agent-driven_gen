import type { ProjectMemberItem } from "../../api/capacity";

interface MemberDetailTableProps {
  data: ProjectMemberItem[] | undefined;
  loading: boolean;
}

export function MemberDetailTable({ data, loading }: MemberDetailTableProps) {
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
        暂无人员数据
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-800">
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">姓名</th>
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">角色</th>
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">部门</th>
            <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">总人天</th>
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">月度分布</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.employee_id} className="border-b border-neutral-900">
              <td className="px-4 py-3 text-sm text-neutral-100">{item.name}</td>
              <td className="px-4 py-3 text-sm text-neutral-400">{item.role}</td>
              <td className="px-4 py-3 text-sm text-neutral-400">{item.department}</td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.total_days.toFixed(1)}
              </td>
              <td className="px-4 py-3 text-sm text-neutral-500">
                {item.monthly_breakdown.map((m) => `${m.month}: ${m.days.toFixed(1)}`).join(" / ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
