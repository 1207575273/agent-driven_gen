import { useState } from "react";
import { DepartmentOverviewPanel } from "../components/departments/DepartmentOverviewPanel";
import { DepartmentSelector } from "../components/departments/DepartmentSelector";
import { MemberDrilldownModal } from "../components/departments/MemberDrilldownModal";
import { MemberRankingTable } from "../components/departments/MemberRankingTable";
import { useDepartmentMembers, useDepartmentOverview } from "../hooks/useDepartments";
import { useFilterOptions } from "../hooks/useFilters";

export default function DepartmentsPage() {
  const filters = useFilterOptions();
  const departments = filters.data?.departments ?? [];

  const [selectedDept, setSelectedDept] = useState<string | null>(
    departments.length > 0 ? (departments[0] ?? null) : null,
  );

  const overview = useDepartmentOverview(selectedDept ? { department: selectedDept } : undefined);
  const members = useDepartmentMembers(selectedDept ? { department: selectedDept } : undefined);

  const [drilldownId, setDrilldownId] = useState<number | null>(null);
  const drilldownMember =
    drilldownId !== null
      ? ((members.data ?? []).find((m) => m.employee_id === drilldownId) ?? null)
      : null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-neutral-100">部门看板</h1>
        <p className="mt-1 text-sm text-neutral-500">
          部门人力投入概览、人员排行榜与偏离度分析, 点击人员下钻查看项目明细。
        </p>
      </div>

      {/* 部门选择 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-3 text-sm text-neutral-400">选择部门</div>
        <DepartmentSelector
          departments={departments}
          selected={selectedDept}
          onSelect={setSelectedDept}
        />
      </div>

      {/* 概览面板 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">部门概况</div>
        <DepartmentOverviewPanel data={overview.data} loading={overview.isLoading} />
      </div>

      {/* 人员排行榜 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">人员排行榜</div>
        <MemberRankingTable
          data={members.data}
          loading={members.isLoading}
          onSelectMember={setDrilldownId}
        />
      </div>

      {/* 人员下钻弹窗 */}
      {drilldownMember ? (
        <MemberDrilldownModal
          employeeId={drilldownMember.employee_id}
          employeeName={drilldownMember.name}
          onClose={() => setDrilldownId(null)}
        />
      ) : null}
    </div>
  );
}
