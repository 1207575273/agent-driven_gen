import { type ReactNode, useState } from "react";
import type { ProjectRankingItem } from "../../api/capacity";

interface ProjectRankingTableProps {
  data: ProjectRankingItem[] | undefined;
  loading: boolean;
  onSelectProject: (name: string) => void;
}

type SortField = keyof Omit<ProjectRankingItem, "project_name">;
type SortDir = "asc" | "desc";

function SortArrow({ active, dir }: { active: boolean; dir: SortDir }) {
  return (
    <span className={`ml-1 inline-block text-xs ${active ? "text-accent" : "text-neutral-600"}`}>
      {active ? (dir === "asc" ? "↑" : "↓") : "↕"}
    </span>
  );
}

function Th({
  field,
  currentField,
  currentDir,
  onSort,
  children,
}: {
  field: SortField;
  currentField: SortField;
  currentDir: SortDir;
  onSort: (f: SortField) => void;
  children: ReactNode;
}) {
  const active = currentField === field;
  const dir = active ? currentDir : "asc";

  return (
    <th
      className="cursor-pointer px-4 py-3 text-left font-mono text-xs text-neutral-400 hover:text-neutral-200 select-none"
      onClick={() => onSort(field)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSort(field);
        }
      }}
    >
      {children}
      <SortArrow active={active} dir={dir} />
    </th>
  );
}

export function ProjectRankingTable({ data, loading, onSelectProject }: ProjectRankingTableProps) {
  const [sortField, setSortField] = useState<SortField>("total_days");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-neutral-600">
        加载中...
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-neutral-600">暂无数据</div>
    );
  }

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const sorted = [...data].sort((a, b) => {
    const av = a[sortField];
    const bv = b[sortField];
    const cmp = typeof av === "number" && typeof bv === "number" ? av - bv : 0;
    return sortDir === "asc" ? cmp : -cmp;
  });

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-800">
            <th className="px-4 py-3 text-left font-mono text-xs text-neutral-400">项目名</th>
            <Th
              field="total_days"
              currentField={sortField}
              currentDir={sortDir}
              onSort={handleSort}
            >
              总人天
            </Th>
            <Th
              field="member_count"
              currentField={sortField}
              currentDir={sortDir}
              onSort={handleSort}
            >
              参与人数
            </Th>
            <Th
              field="avg_days_per_person"
              currentField={sortField}
              currentDir={sortDir}
              onSort={handleSort}
            >
              平均人天
            </Th>
            <Th
              field="concentration"
              currentField={sortField}
              currentDir={sortDir}
              onSort={handleSort}
            >
              资源浓度
            </Th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((item) => (
            <tr
              key={item.project_name}
              className="cursor-pointer border-b border-neutral-900 transition-colors hover:bg-neutral-900/50"
              onClick={() => onSelectProject(item.project_name)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectProject(item.project_name);
                }
              }}
            >
              <td className="max-w-[240px] truncate px-4 py-3 text-sm text-neutral-100">
                {item.project_name}
              </td>
              <td className="px-4 py-3 font-mono text-sm tabular-nums text-neutral-100">
                {item.total_days.toLocaleString()}
              </td>
              <td className="px-4 py-3 font-mono text-sm tabular-nums text-neutral-100">
                {item.member_count}
              </td>
              <td className="px-4 py-3 font-mono text-sm tabular-nums text-neutral-100">
                {item.avg_days_per_person.toFixed(1)}
              </td>
              <td className="px-4 py-3 font-mono text-sm tabular-nums text-neutral-100">
                {item.concentration.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
