import type { DeptCategoryMatrix } from "../../api/capacity";
import { useMatrix } from "../../hooks/useCapacity";
import { Heatmap } from "../charts/Heatmap";
import { LoadingSpinner } from "../shared/LoadingSpinner";

export function MatrixPanel() {
  const { data, isLoading, isError } = useMatrix();

  if (isLoading) return <LoadingSpinner />;
  if (isError || !data) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-neutral-600 border border-dashed border-neutral-800 rounded-lg">
        暂无综合交叉矩阵数据
      </div>
    );
  }

  const matrixData: DeptCategoryMatrix = data;

  return (
    <div>
      <h3 className="text-sm font-medium text-neutral-400 mb-3">部门x分类矩阵</h3>
      <div className="rounded-lg border border-neutral-800/50 bg-neutral-900/30 p-4">
        <Heatmap
          xLabels={matrixData.categories}
          yLabels={matrixData.depts}
          data={matrixData.matrix}
          height={Math.max(280, matrixData.depts.length * 50 + 80)}
        />
      </div>
    </div>
  );
}
