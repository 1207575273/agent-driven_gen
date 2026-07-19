import { useState } from "react";
import { DeptCategoryPanel } from "../components/capacity/DeptCategoryPanel";
import { FilterBar } from "../components/capacity/FilterBar";
import { MatrixPanel } from "../components/capacity/MatrixPanel";
import { PersonCategoryPanel } from "../components/capacity/PersonCategoryPanel";
import { RoleCategoryPanel } from "../components/capacity/RoleCategoryPanel";
import { ThreeFastComparison } from "../components/capacity/ThreeFastComparison";
import { TimeCategoryPanel } from "../components/capacity/TimeCategoryPanel";

type TabKey = "time-category" | "dept-category" | "role-category" | "person" | "matrix";

const TABS: { key: TabKey; label: string }[] = [
  { key: "time-category", label: "时间x分类" },
  { key: "dept-category", label: "组织x分类" },
  { key: "role-category", label: "角色x分类" },
  { key: "person", label: "人员维度" },
  { key: "matrix", label: "综合交叉" },
];

export function CrossAnalysisPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("time-category");

  return (
    <div>
      <h1 className="text-xl font-semibold text-neutral-100 mb-4">产能交叉维度分析</h1>

      <FilterBar showCategoryLevel />

      {/* Tabs */}
      <div className="flex border-b border-neutral-800 mb-6">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab.key
                ? "border-accent text-accent"
                : "border-transparent text-neutral-500 hover:text-neutral-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div>
        {activeTab === "time-category" && <TimeCategoryPanel />}
        {activeTab === "dept-category" && <DeptCategoryPanel />}
        {activeTab === "role-category" && <RoleCategoryPanel />}
        {activeTab === "person" && <PersonCategoryPanel />}
        {activeTab === "matrix" && (
          <div className="space-y-6">
            <MatrixPanel />
            <ThreeFastComparison />
          </div>
        )}
      </div>
    </div>
  );
}
