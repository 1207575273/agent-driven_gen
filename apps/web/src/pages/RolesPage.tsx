import { PersonnelStructurePieChart } from "../components/roles/PersonnelStructurePieChart";
import { RoleAggregationTable } from "../components/roles/RoleAggregationTable";
import { RoleDeptDistributionChart } from "../components/roles/RoleDeptDistributionChart";
import { useRoleAggregation, useRoleStructure } from "../hooks/useRoles";

export default function RolesPage() {
  const aggregation = useRoleAggregation();
  const structure = useRoleStructure();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-neutral-100">角色分析</h1>
        <p className="mt-1 text-sm text-neutral-500">按角色聚合的投入分布与人力结构占比。</p>
      </div>

      {/* 角色聚合表 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">角色聚合</div>
        <RoleAggregationTable data={aggregation.data} loading={aggregation.isLoading} />
      </div>

      {/* 角色下部门分布堆叠柱状图 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">角色 x 部门分布(按人数)</div>
        <RoleDeptDistributionChart data={aggregation.data} loading={aggregation.isLoading} />
      </div>

      {/* 人力结构饼图 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">人力结构</div>
        <PersonnelStructurePieChart data={structure.data} loading={structure.isLoading} />
      </div>
    </div>
  );
}
