import { useState } from "react";
import { ProjectDrilldownModal } from "../components/projects/ProjectDrilldownModal";
import { ProjectRankingBarChart } from "../components/projects/ProjectRankingBarChart";
import { ProjectRankingTable } from "../components/projects/ProjectRankingTable";
import { useProjectRanking } from "../hooks/useProjects";

export default function ProjectsPage() {
  const { data, isLoading } = useProjectRanking();
  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-semibold text-neutral-100">项目看板</h1>
        <p className="mt-1 text-sm text-neutral-500">
          项目投入排名与资源分布, 点击项目下钻查看人员明细。
        </p>
      </div>

      {/* 柱状图 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">项目投入 Top 15</div>
        <ProjectRankingBarChart data={data} loading={isLoading} />
      </div>

      {/* 排名表格 */}
      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40 p-5">
        <div className="mb-4 text-sm text-neutral-400">项目排行榜</div>
        <ProjectRankingTable data={data} loading={isLoading} onSelectProject={setSelectedProject} />
      </div>

      {/* 下钻弹窗 */}
      {selectedProject ? (
        <ProjectDrilldownModal
          projectName={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      ) : null}
    </div>
  );
}
