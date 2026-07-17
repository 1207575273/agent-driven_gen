// 产能分析系统 API 封装: 所有 14 个端点, 只用 GET。筛选参数通过 query params 传递。

const BASE = "/api/v1";

async function request<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE}${path}`);
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${await resp.text()}`);
  }
  return resp.json() as Promise<T>;
}

// ---- 类型定义 ----

export interface FilterParams {
  start_date?: string;
  end_date?: string;
  department?: string;
  role?: string;
  personnel_type?: string;
  project?: string;
  level?: number;
}

export interface SummaryResponse {
  total_person_days: number;
  reporter_count: number;
  project_count: number;
  department_count: number;
}

export interface MonthlyTrendItem {
  month: string;
  total_days: number;
}

export interface ProjectRankingItem {
  project_name: string;
  total_days: number;
  member_count: number;
  avg_days_per_person: number;
  concentration: number;
}

export interface MonthlyBreakdown {
  month: string;
  days: number;
}

export interface ProjectMemberItem {
  employee_id: number;
  name: string;
  role: string;
  department: string;
  total_days: number;
  monthly_breakdown: MonthlyBreakdown[];
}

export interface DepartmentOverview {
  total_person_days: number;
  avg_person_days: number;
  member_count: number;
  project_distribution: {
    project_name: string;
    total_days: number;
    percentage: number;
  }[];
  top_n_concentration: {
    top3_percentage: number;
    top5_percentage: number;
  };
}

export interface DepartmentMemberItem {
  employee_id: number;
  name: string;
  role: string;
  department: string;
  total_days: number;
  peer_avg_days: number;
  deviation: number;
  deviation_level: "normal" | "yellow" | "red";
}

export interface MemberProjectItem {
  project_name: string;
  total_days: number;
  monthly_breakdown: MonthlyBreakdown[];
}

export interface DeptDistributionItem {
  department: string;
  person_count: number;
  total_days: number;
}

export interface RoleAggregationItem {
  role: string;
  total_days: number;
  person_count: number;
  dept_distribution: DeptDistributionItem[];
}

export interface StructureItem {
  employee_status: string;
  total_days: number;
  person_count: number;
  percentage: number;
}

export interface FilterOptions {
  departments: string[];
  roles: string[];
  personnel_types: string[];
  employee_statuses: string[];
  projects: string[];
  date_range: { min: string; max: string };
}

// ---- 辅助: 将 FilterParams 转为 query string ----

function toQuery(filters: FilterParams = {}): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

// ---- 4.1 仪表盘 ----

export const dashboardApi = {
  summary: (filters?: FilterParams) =>
    request<SummaryResponse>(`/dashboard/summary${toQuery(filters)}`),
  monthlyTrend: (filters?: FilterParams) =>
    request<MonthlyTrendItem[]>(`/dashboard/monthly-trend${toQuery(filters)}`),
};

// ---- 4.2 项目投入看板 ----

export const projectsApi = {
  ranking: (filters?: FilterParams) =>
    request<ProjectRankingItem[]>(`/projects/ranking${toQuery(filters)}`),
  members: (projectName: string, filters?: FilterParams) =>
    request<ProjectMemberItem[]>(
      `/projects/${encodeURIComponent(projectName)}/members${toQuery(filters)}`,
    ),
  monthlyTrend: (projectName: string, filters?: FilterParams) =>
    request<MonthlyTrendItem[]>(
      `/projects/${encodeURIComponent(projectName)}/monthly-trend${toQuery(filters)}`,
    ),
};

// ---- 4.3 部门/团队看板 ----

export const departmentsApi = {
  overview: (filters?: FilterParams) =>
    request<DepartmentOverview>(`/departments/overview${toQuery(filters)}`),
  members: (filters?: FilterParams) =>
    request<DepartmentMemberItem[]>(`/departments/members${toQuery(filters)}`),
  memberProjects: (employeeId: number, filters?: FilterParams) =>
    request<MemberProjectItem[]>(`/departments/members/${employeeId}/projects${toQuery(filters)}`),
};

// ---- 4.4 角色维度分析 ----

export const rolesApi = {
  aggregation: (filters?: FilterParams) =>
    request<RoleAggregationItem[]>(`/roles/aggregation${toQuery(filters)}`),
  structure: (filters?: FilterParams) =>
    request<StructureItem[]>(`/roles/structure${toQuery(filters)}`),
};

// ---- 4.5 筛选器选项 ----

export const filtersApi = {
  options: () => request<FilterOptions>("/filters/options"),
};
