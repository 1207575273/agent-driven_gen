import { useState } from "react";
import { AbnormalDetailList } from "../components/capacity/AbnormalDetailList";
import { AuditSummaryCards } from "../components/capacity/AuditSummaryCards";
import { DepartmentFillRateTable } from "../components/capacity/DepartmentFillRateTable";
import { DeviationRankingTable } from "../components/capacity/DeviationRankingTable";
import { FilterBar } from "../components/capacity/FilterBar";
import { MonthlyTrendChart } from "../components/capacity/MonthlyTrendChart";
import { ZeroFillingList } from "../components/capacity/ZeroFillingList";

type TabKey = "dashboard" | "fill-rate" | "zero-fill" | "deviation" | "abnormal-detail";

const TABS: { key: TabKey; label: string }[] = [
  { key: "dashboard", label: "应有产能看板" },
  { key: "fill-rate", label: "填报率分析" },
  { key: "zero-fill", label: "零填报识别" },
  { key: "deviation", label: "偏差异常排行" },
  { key: "abnormal-detail", label: "异常人员明细" },
];

export function CapacityAuditPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("dashboard");

  return (
    <div>
      <h1 className="text-xl font-semibold text-neutral-100 mb-4">产能填报审计</h1>

      <FilterBar />

      {/* KPI Cards - always visible */}
      <AuditSummaryCards />

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
        {activeTab === "dashboard" && (
          <section>
            <h2 className="text-sm font-medium text-neutral-400 mb-3">月度应有 vs 实际趋势</h2>
            <MonthlyTrendChart />
          </section>
        )}

        {activeTab === "fill-rate" && (
          <section>
            <h2 className="text-sm font-medium text-neutral-400 mb-3">
              部门填报率排行（点击部门下钻）
            </h2>
            <DepartmentFillRateTable />
          </section>
        )}

        {activeTab === "deviation" && (
          <section>
            <h2 className="text-sm font-medium text-neutral-400 mb-3">个人偏差排行</h2>
            <DeviationRankingTable />
          </section>
        )}

        {activeTab === "zero-fill" && (
          <section>
            <h2 className="text-sm font-medium text-neutral-400 mb-3">零填报人员</h2>
            <ZeroFillingList />
          </section>
        )}

        {activeTab === "abnormal-detail" && (
          <section>
            <h2 className="text-sm font-medium text-neutral-400 mb-3">
              异常人员明细（标红人员列表）
            </h2>
            <AbnormalDetailList />
          </section>
        )}
      </div>
    </div>
  );
}
