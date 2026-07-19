// 产能分析系统 API 类型定义与封装。
// 仅用 GET / POST，与后端约定一致。

import { request } from "./client";

// ── 审计汇总 ──
export interface AuditSummary {
  should_be_days: number;
  actual_days: number;
  fill_rate: number;
  deviation: number;
  employee_count: number;
  zero_fill_count: number;
  abnormal_count: number;
}

// ── 月度趋势 ──
export interface MonthlyTrend {
  month: string;
  should_be_days: number;
  actual_days: number;
  fill_rate: number;
  deviation: number;
  working_days: number;
}

// ── 部门填报率 ──
export interface DepartmentFillRate {
  dept_name: string;
  dept_path: string;
  dept_level: number;
  should_be_days: number;
  actual_days: number;
  fill_rate: number;
  deviation: number;
  abnormal_count: number;
  person_count: number;
  has_children: boolean;
}

// ── 零填报人员 ──
export interface ZeroFillingPerson {
  employee_id: number;
  name: string;
  employee_id_str: string;
  dept_name: string;
  dept_path: string;
  role: string;
  should_be_days: number;
  actual_days: number;
  entry_date: string | null;
  fill_note: string | null;
}

// ── 偏差排行 ──
export interface PersonDeviation {
  employee_id: number;
  name: string;
  employee_id_str: string;
  dept_name: string;
  dept_path: string;
  role: string;
  should_be_days: number;
  actual_days: number;
  deviation: number;
  deviation_rate: number;
  is_abnormal: boolean;
  project_count?: number;
}

// ── 人员月度明细 ──
export interface PersonMonthlyData {
  month: string;
  should_be_days: number;
  actual_days: number;
  deviation: number;
  fill_rate: number;
}

export interface PersonMonthly {
  employee_id: number;
  name: string;
  monthly_data: PersonMonthlyData[];
}

// ── 人员项目投入 ──
export interface MonthlyBreakdown {
  month: string;
  days: number;
}

export interface PersonProjectItem {
  project_name: string;
  category_path: string;
  category_id: number;
  person_days: number;
  monthly_breakdown: MonthlyBreakdown[];
}

// ── 时间 x 分类 ──
export interface ChildCategory {
  category_id: number;
  category_name: string;
  person_days: number;
}

export interface CategoryPieSlice {
  category_name: string;
  total_days: number;
  percentage: number;
}

export interface TimeCategoryItem {
  time_label: string;
  person_days: number;
  categories: CategoryPieSlice[];
}

// ── 应有 vs 实际(按时间) ──
export interface ShouldVsActualItem {
  time_label: string;
  should_be_days: number;
  actual_days: number;
  fill_rate: number;
  deviation: number;
}

// ── 部门 x 分类 ──
export interface DeptCategoryDistribution {
  [categoryName: string]: number;
}

export interface DeptCategoryItem {
  dept_name: string;
  dept_path: string;
  category_distribution: DeptCategoryDistribution;
  total_days: number;
  person_count: number;
  fill_rate: number;
  has_children: boolean;
}

// ── 部门分类热力图 ──
export interface DeptCategoryMatrix {
  depts: string[];
  categories: string[];
  matrix: number[][];
}

// ── 角色 x 分类 ──
export interface RoleCategoryItem {
  role: string;
  person_count: number;
  total_days: number;
  avg_days_per_person: number;
  category_distribution: DeptCategoryDistribution;
}

// ── 角色月度趋势 ──
export interface RoleMonthlyTrendItem {
  month: string;
  category_distribution: DeptCategoryDistribution;
  total_days: number;
}

// ── 人员排名 ──
export interface PersonRankingItem {
  employee_id: number;
  name: string;
  employee_id_str: string;
  dept_name: string;
  dept_path: string;
  role: string;
  actual_days: number;
  should_be_days: number;
  deviation: number;
  project_count: number;
}

// ── 人员 x 分类 ──
export interface PersonCategoryItem {
  employee_id: number;
  name: string;
  employee_id_str: string;
  dept_name: string;
  dept_path: string;
  role: string;
  total_days: number;
  project_count: number;
  category_distribution: DeptCategoryDistribution;
}

// ── 三快计划对比 ──
export interface ThreeFastComparisonItem {
  quarter: string;
  category_name: string;
  category_id: number;
  plan_days: number;
  actual_days: number;
  deviation: number;
  achieve_rate: number;
}

// ── 下钻: 工时明细记录 ──
export interface DrillDownRecord {
  id: number;
  project_name: string;
  matched_project_name: string;
  reporter: string;
  reporter_department: string;
  report_date: string;
  hours: number;
  description: string;
  category_path: string | null;
  employee_id: number;
}

// ── 下钻: 子部门 ──
export interface DeptChildren {
  dept_name: string;
  dept_path: string;
  dept_level: number;
  person_count: number;
  total_actual_days: number;
  has_children: boolean;
}

// ── 下钻: 分类项目 ──
export interface CategoryProjectItem {
  project_name: string;
  person_days: number;
  person_count: number;
  percentage: number;
}

// ── 筛选器选项 ──
export interface FilterTimeRange {
  min_month: string;
  max_month: string;
  available_quarters: string[];
  available_halfs: string[];
}

export interface FilterDepartmentLevels {
  level1: string[];
  level2: string[];
  level3: string[];
  level4: string[];
}

export interface FilterDeptOption {
  dept_name: string;
  dept_path: string;
}

export interface FilterCategoryOption {
  id: number;
  name: string;
  children?: FilterCategoryOption[];
}

export interface FilterOptions {
  time_range: FilterTimeRange;
  departments: FilterDepartmentLevels;
  roles: string[];
  categories: {
    level1: FilterCategoryOption[];
  };
}

// ── 导入结果 ──
export interface ImportStats {
  employees_imported: number;
  work_hours_imported: number;
  categories_imported: number;
  holidays_imported: number;
  capacity_records_created: number;
  employee_match_rate: number;
  project_match_rate: number;
  unmatched_projects: string[];
  errors: string[];
}

export interface ImportResult {
  success: boolean;
  stats: ImportStats;
}

export interface RematchResult {
  success: boolean;
  rematched_count: number;
  unmatched_count: number;
  unmatched_projects: string[];
}

// ── 辅助函数：构建 query string ──
function buildParams(params: Record<string, string | number | boolean | null | undefined>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined) {
      searchParams.append(key, String(value));
    }
  }
  return searchParams.toString();
}

// ── 产能审计 API ──
export const capacityAuditApi = {
  getSummary: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<AuditSummary>(`/capacity-audit/summary?${buildParams(params)}`),

  getMonthlyTrend: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<MonthlyTrend[]>(`/capacity-audit/monthly-trend?${buildParams(params)}`),

  getDepartmentFillRates: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DepartmentFillRate[]>(`/capacity-audit/department-fill-rate?${buildParams(params)}`),

  getZeroFillingList: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<ZeroFillingPerson[]>(`/capacity-audit/zero-filling?${buildParams(params)}`),

  getDeviationRanking: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<PersonDeviation[]>(`/capacity-audit/deviation-ranking?${buildParams(params)}`),

  getAbnormalDetail: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<PersonDeviation[]>(`/capacity-audit/abnormal-detail?${buildParams(params)}`),

  getPersonMonthly: (employeeId: number) =>
    request<PersonMonthly>(`/capacity-audit/person-monthly?employee_id=${employeeId}`),

  getPersonProjects: (employeeId: number, timePeriod?: string) => {
    const qs = timePeriod
      ? `employee_id=${employeeId}&time_period=${encodeURIComponent(timePeriod)}`
      : `employee_id=${employeeId}`;
    return request<PersonProjectItem[]>(`/capacity-audit/person-projects?${qs}`);
  },
};

// ── 交叉分析 API ──
export const crossAnalysisApi = {
  getTimeCategory: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<TimeCategoryItem[]>(`/cross-analysis/time-category?${buildParams(params)}`),

  getShouldVsActual: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<ShouldVsActualItem[]>(`/cross-analysis/should-vs-actual?${buildParams(params)}`),

  getDeptCategory: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DeptCategoryItem[]>(`/cross-analysis/dept-category?${buildParams(params)}`),

  getDeptCategoryMatrix: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DeptCategoryMatrix>(`/cross-analysis/dept-category-matrix?${buildParams(params)}`),

  getRoleCategory: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<RoleCategoryItem[]>(`/cross-analysis/role-category?${buildParams(params)}`),

  getRoleMonthlyTrend: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<RoleMonthlyTrendItem[]>(`/cross-analysis/role-monthly-trend?${buildParams(params)}`),

  getPersonRanking: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<PersonRankingItem[]>(`/cross-analysis/person-ranking?${buildParams(params)}`),

  getMatrix: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DeptCategoryMatrix>(`/cross-analysis/matrix?${buildParams(params)}`),

  getPersonCategory: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<PersonCategoryItem[]>(`/cross-analysis/person-category?${buildParams(params)}`),

  getThreeFastComparison: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<ThreeFastComparisonItem[]>(
      `/cross-analysis/three-fast-comparison?${buildParams(params)}`,
    ),
};

// ── 下钻 API ──
export const drillDownApi = {
  getRecords: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DrillDownRecord[]>(`/drill-down/records?${buildParams(params)}`),

  getDeptChildren: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<DeptChildren[]>(`/drill-down/dept-children?${buildParams(params)}`),

  getCategoryProjects: (params: Record<string, string | number | boolean | null | undefined>) =>
    request<CategoryProjectItem[]>(`/drill-down/category-projects?${buildParams(params)}`),
};

// ── 筛选器 API ──
export const filterApi = {
  getOptions: () => request<FilterOptions>("/filters/options"),
};

// ── 数据导入 API ──
export const dataImportApi = {
  import: (formData: FormData) =>
    request<ImportResult>("/data-import/import", {
      method: "POST",
      body: formData,
      headers: {} as Record<string, string>,
    }),

  rematchCategories: () =>
    request<RematchResult>("/data-import/rematch-categories", { method: "POST" }),
};
