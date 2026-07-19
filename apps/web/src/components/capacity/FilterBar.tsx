import { useFilterOptions } from "../../hooks/useCapacity";
import { useFilterStore } from "../../stores/useFilterStore";

const GRANULARITY_OPTIONS = [
  { value: "month" as const, label: "月" },
  { value: "quarter" as const, label: "季" },
  { value: "half" as const, label: "半年" },
];

const DUAL_TIME_PERIODS = [
  { value: "2026-H1", label: "2026H1" },
  { value: "2026-Q1", label: "2026Q1" },
  { value: "2026-Q2", label: "2026Q2" },
];

const MONTH_TIME_PERIODS = [
  { value: "2026-01", label: "1月" },
  { value: "2026-02", label: "2月" },
  { value: "2026-03", label: "3月" },
  { value: "2026-04", label: "4月" },
  { value: "2026-05", label: "5月" },
  { value: "2026-06", label: "6月" },
];

const DEPT_LEVELS = [
  { value: 1, label: "一级" },
  { value: 2, label: "二级" },
  { value: 3, label: "三级" },
  { value: 4, label: "四级" },
];

const selectBaseClass =
  "rounded-md border border-neutral-700 bg-neutral-900 px-2 py-1.5 text-xs text-neutral-200 outline-none focus:border-accent transition-colors";

interface FilterBarProps {
  showRole?: boolean;
  showCategoryLevel?: boolean;
}

export function FilterBar({ showRole = true, showCategoryLevel = false }: FilterBarProps) {
  const {
    timeGranularity,
    timePeriod,
    deptLevel,
    deptName,
    role,
    categoryLevel,
    setFilter,
    resetFilters,
  } = useFilterStore();

  const { data: filterOptions } = useFilterOptions();

  const timePeriodOptions = timeGranularity === "month" ? MONTH_TIME_PERIODS : DUAL_TIME_PERIODS;

  const handleGranularityChange = (value: string) => {
    setFilter("timeGranularity", value);
    if (value === "month") {
      setFilter("timePeriod", "2026-01");
    } else {
      setFilter("timePeriod", "2026-H1");
    }
  };

  // Depts according to selected level — fetch from API (returns plain string[])
  const deptOptions: string[] =
    filterOptions && deptLevel
      ? (() => {
          const levelKey = `level${deptLevel}` as keyof typeof filterOptions.departments;
          return filterOptions.departments[levelKey] ?? [];
        })()
      : [];

  // Roles from API
  const roleOptions: string[] = filterOptions?.roles ?? [];

  return (
    <div className="flex flex-wrap items-end gap-3 mb-6">
      {/* Time granularity */}
      <div className="flex flex-col gap-1">
        <span className="text-[10px] font-medium text-neutral-500 uppercase">粒度</span>
        <div className="flex rounded-md border border-neutral-700 overflow-hidden">
          {GRANULARITY_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => handleGranularityChange(opt.value)}
              className={`px-2.5 py-1.5 text-xs transition-colors ${
                timeGranularity === opt.value
                  ? "bg-accent/20 text-accent"
                  : "bg-neutral-900 text-neutral-500 hover:text-neutral-300"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Time period */}
      <label className="flex flex-col gap-1">
        <span className="text-[10px] font-medium text-neutral-500 uppercase">时段</span>
        <select
          value={timePeriod ?? ""}
          onChange={(e) => setFilter("timePeriod", e.target.value)}
          className={selectBaseClass}
        >
          {timePeriodOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      {/* Dept level */}
      <label className="flex flex-col gap-1">
        <span className="text-[10px] font-medium text-neutral-500 uppercase">部门层级</span>
        <select
          value={deptLevel ?? ""}
          onChange={(e) => {
            const val = e.target.value;
            setFilter("deptLevel", val ? Number(val) : null);
            setFilter("deptName", null);
          }}
          className={selectBaseClass}
        >
          {DEPT_LEVELS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>

      {/* Dept name —下拉框：联动 deptLevel */}
      {deptLevel && (
        <label className="flex flex-col gap-1">
          <span className="text-[10px] font-medium text-neutral-500 uppercase">部门</span>
          <select
            value={deptName ?? ""}
            onChange={(e) => setFilter("deptName", e.target.value || null)}
            className={`${selectBaseClass} max-w-[160px]`}
          >
            <option value="">全部部门</option>
            {deptOptions.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
      )}

      {/* Role — 下拉框 */}
      {showRole && (
        <label className="flex flex-col gap-1">
          <span className="text-[10px] font-medium text-neutral-500 uppercase">角色</span>
          <select
            value={role ?? ""}
            onChange={(e) => setFilter("role", e.target.value || null)}
            className={`${selectBaseClass} max-w-[140px]`}
          >
            <option value="">全部角色</option>
            {roleOptions.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
      )}

      {/* Category level */}
      {showCategoryLevel && (
        <label className="flex flex-col gap-1">
          <span className="text-[10px] font-medium text-neutral-500 uppercase">项目分类</span>
          <select
            value={categoryLevel}
            onChange={(e) => setFilter("categoryLevel", Number(e.target.value))}
            className={selectBaseClass}
          >
            <option value={1}>大类</option>
            <option value={2}>分类</option>
            <option value={3}>细分</option>
          </select>
        </label>
      )}

      {/* Reset */}
      <button
        type="button"
        onClick={resetFilters}
        className="rounded-md border border-neutral-700 px-3 py-1.5 text-xs text-neutral-500 hover:text-neutral-200 hover:border-neutral-600 transition-colors ml-auto"
      >
        重置
      </button>
    </div>
  );
}
