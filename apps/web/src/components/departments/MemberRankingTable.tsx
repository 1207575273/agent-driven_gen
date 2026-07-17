import type { DepartmentMemberItem } from "../../api/capacity";
import { DeviationBadge } from "./DeviationBadge";

interface MemberRankingTableProps {
  data: DepartmentMemberItem[] | undefined;
  loading: boolean;
  onSelectMember: (employeeId: number) => void;
}

export function MemberRankingTable({ data, loading, onSelectMember }: MemberRankingTableProps) {
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
            <th className="px-4 py-3 text-right font-mono text-xs text-neutral-400">同级均值</th>
            <th className="px-4 py-3 text-center font-mono text-xs text-neutral-400">偏离度</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr
              key={item.employee_id}
              className="cursor-pointer border-b border-neutral-900 transition-colors hover:bg-neutral-900/50"
              onClick={() => onSelectMember(item.employee_id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectMember(item.employee_id);
                }
              }}
            >
              <td className="px-4 py-3 text-sm text-neutral-100">{item.name}</td>
              <td className="px-4 py-3 text-sm text-neutral-400">{item.role}</td>
              <td className="px-4 py-3 text-sm text-neutral-400">{item.department}</td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.total_days.toFixed(1)}
              </td>
              <td className="px-4 py-3 text-right font-mono text-sm tabular-nums text-neutral-100">
                {item.peer_avg_days.toFixed(1)}
              </td>
              <td className="px-4 py-3 text-center">
                <DeviationBadge deviationLevel={item.deviation_level} deviation={item.deviation} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
