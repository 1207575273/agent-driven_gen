import { useQuery } from "@tanstack/react-query";
import { capacityAuditApi, crossAnalysisApi, drillDownApi, filterApi } from "../api/capacity";
import { useFilterStore } from "../stores/useFilterStore";

// ── 产能审计 hooks ──

export function useAuditSummary() {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  return useQuery({
    queryKey: ["audit-summary", timePeriod, deptLevel, deptName, role],
    queryFn: () =>
      capacityAuditApi.getSummary({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useMonthlyTrend() {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  return useQuery({
    queryKey: ["monthly-trend", timePeriod, deptLevel, deptName, role],
    queryFn: () =>
      capacityAuditApi.getMonthlyTrend({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useDepartmentFillRates(parentDept?: string) {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  const effectiveLevel = parentDept ? (deptLevel ?? 2) + 1 : (deptLevel ?? 2);
  return useQuery({
    queryKey: ["dept-fill-rates", timePeriod, effectiveLevel, deptName, role, parentDept],
    queryFn: () =>
      capacityAuditApi.getDepartmentFillRates({
        time_period: timePeriod,
        dept_level: effectiveLevel,
        dept_name: deptName,
        parent_dept: parentDept ?? null,
        role,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useZeroFillingList() {
  const { timePeriod, deptLevel, deptName } = useFilterStore();
  return useQuery({
    queryKey: ["zero-filling", timePeriod, deptLevel, deptName],
    queryFn: () =>
      capacityAuditApi.getZeroFillingList({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useDeviationRanking(params: {
  deviationDirection?: string;
  sortBy?: string;
  sortDir?: string;
  isAbnormalOnly?: boolean;
}) {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  return useQuery({
    queryKey: [
      "deviation-ranking",
      timePeriod,
      deptLevel,
      deptName,
      role,
      params.deviationDirection,
      params.sortBy,
      params.sortDir,
      params.isAbnormalOnly,
    ],
    queryFn: () =>
      capacityAuditApi.getDeviationRanking({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
        deviation_direction: params.deviationDirection ?? "all",
        sort_by: params.sortBy ?? "deviation_abs",
        sort_dir: params.sortDir ?? "desc",
        is_abnormal_only: params.isAbnormalOnly ?? false,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useAbnormalDetail() {
  const { timePeriod, deptLevel, deptName } = useFilterStore();
  return useQuery({
    queryKey: ["abnormal-detail", timePeriod, deptLevel, deptName],
    queryFn: () =>
      capacityAuditApi.getAbnormalDetail({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function usePersonMonthly(employeeId: number | null) {
  return useQuery({
    queryKey: ["person-monthly", employeeId],
    queryFn: () => {
      if (employeeId === null) throw new Error("employeeId required");
      return capacityAuditApi.getPersonMonthly(employeeId);
    },
    enabled: employeeId !== null,
  });
}

export function usePersonProjects(employeeId: number | null, timePeriod?: string) {
  return useQuery({
    queryKey: ["person-projects", employeeId, timePeriod],
    queryFn: () => {
      if (employeeId === null) throw new Error("employeeId required");
      return capacityAuditApi.getPersonProjects(employeeId, timePeriod);
    },
    enabled: employeeId !== null,
  });
}

// ── 交叉分析 hooks ──

export function useTimeCategory(categoryLevel?: number, parentCategoryId?: number) {
  const { timeGranularity, timePeriod, deptLevel, deptName, role } =
    useFilterStore();
  const level = categoryLevel ?? 1;
  return useQuery({
    queryKey: [
      "time-category",
      timeGranularity,
      timePeriod,
      deptLevel,
      deptName,
      role,
      level,
      parentCategoryId,
    ],
    queryFn: () =>
      crossAnalysisApi.getTimeCategory({
        time_granularity: timeGranularity,
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
        category_level: level,
        parent_category_id: parentCategoryId ?? undefined,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useShouldVsActual() {
  const { timeGranularity, timePeriod, deptLevel, deptName } = useFilterStore();
  return useQuery({
    queryKey: ["should-vs-actual", timeGranularity, timePeriod, deptLevel, deptName],
    queryFn: () =>
      crossAnalysisApi.getShouldVsActual({
        time_granularity: timeGranularity,
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useDeptCategory(categoryLevel?: number, parentCategoryId?: number) {
  const { timePeriod, deptLevel, deptName } = useFilterStore();
  const level = categoryLevel ?? 1;
  return useQuery({
    queryKey: ["dept-category", timePeriod, deptLevel, deptName, level, parentCategoryId],
    queryFn: () =>
      crossAnalysisApi.getDeptCategory({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        category_level: level,
        parent_category_id: parentCategoryId ?? undefined,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useDeptCategoryMatrix() {
  const { timePeriod, deptLevel, categoryLevel } = useFilterStore();
  return useQuery({
    queryKey: ["dept-category-matrix", timePeriod, deptLevel, categoryLevel],
    queryFn: () =>
      crossAnalysisApi.getDeptCategoryMatrix({
        time_period: timePeriod,
        dept_level: deptLevel,
        category_level: categoryLevel,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useRoleCategory(categoryLevel?: number, parentCategoryId?: number) {
  const { timePeriod, deptLevel, deptName } = useFilterStore();
  const level = categoryLevel ?? 1;
  return useQuery({
    queryKey: ["role-category", timePeriod, deptLevel, deptName, level, parentCategoryId],
    queryFn: () =>
      crossAnalysisApi.getRoleCategory({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        category_level: level,
        parent_category_id: parentCategoryId ?? undefined,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useRoleMonthlyTrend(role: string | null) {
  const { timePeriod, categoryLevel } = useFilterStore();
  return useQuery({
    queryKey: ["role-monthly-trend", timePeriod, role, categoryLevel],
    queryFn: () =>
      crossAnalysisApi.getRoleMonthlyTrend({
        time_period: timePeriod,
        role: role ?? "",
        category_level: categoryLevel,
      }),
    enabled: Boolean(timePeriod && role),
  });
}

export function usePersonRanking(params: {
  sortBy?: string;
  sortDir?: string;
}) {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  return useQuery({
    queryKey: [
      "person-ranking",
      timePeriod,
      deptLevel,
      deptName,
      role,
      params.sortBy,
      params.sortDir,
    ],
    queryFn: () =>
      crossAnalysisApi.getPersonRanking({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
        sort_by: params.sortBy ?? "actual_days",
        sort_dir: params.sortDir ?? "desc",
      }),
    enabled: Boolean(timePeriod),
  });
}

export function usePersonCategory(categoryLevel?: number, parentCategoryId?: number) {
  const { timePeriod, deptLevel, deptName, role } = useFilterStore();
  const level = categoryLevel ?? 1;
  return useQuery({
    queryKey: ["person-category", timePeriod, deptLevel, deptName, role, level, parentCategoryId],
    queryFn: () =>
      crossAnalysisApi.getPersonCategory({
        time_period: timePeriod,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
        category_level: level,
        parent_category_id: parentCategoryId ?? undefined,
      }),
    enabled: Boolean(timePeriod),
  });
}

export function useThreeFastComparison() {
  const { timePeriod } = useFilterStore();
  return useQuery({
    queryKey: ["three-fast-comparison", timePeriod],
    queryFn: () =>
      crossAnalysisApi.getThreeFastComparison({
        time_period: timePeriod,
      }),
    enabled: Boolean(timePeriod),
  });
}

// ── 综合交叉矩阵 hook ──

export function useMatrix() {
  const { timePeriod, deptLevel, deptName, role, categoryLevel } = useFilterStore();
  return useQuery({
    queryKey: ["matrix", timePeriod, deptLevel, deptName, role, categoryLevel],
    queryFn: () =>
      crossAnalysisApi.getMatrix({
        time_period: timePeriod,
        row_dimension: "dept",
        col_dimension: "category",
        category_level: categoryLevel,
        dept_level: deptLevel,
        dept_name: deptName,
        role,
      }),
    enabled: Boolean(timePeriod),
  });
}

// ── 下钻 hooks ──

export function useDrillDownRecords(params: Record<string, string | number | null | undefined>) {
  const hasParams = Object.values(params).some((v) => v !== null && v !== undefined);
  return useQuery({
    queryKey: ["drill-records", params],
    queryFn: () => drillDownApi.getRecords(params),
    enabled: hasParams,
  });
}

export function useDeptChildren(params: {
  timePeriod?: string | null;
  parentDept?: string;
  deptLevel?: number;
}) {
  return useQuery({
    queryKey: ["dept-children", params],
    queryFn: () =>
      drillDownApi.getDeptChildren({
        time_period: params.timePeriod ?? null,
        parent_dept: params.parentDept ?? null,
        dept_level: params.deptLevel ?? null,
      }),
    enabled: Boolean(params.parentDept),
  });
}

export function useCategoryProjects(params: {
  timePeriod?: string | null;
  categoryId?: number | null;
  deptLevel?: number | null;
  deptName?: string | null;
  role?: string | null;
}) {
  return useQuery({
    queryKey: ["category-projects", params],
    queryFn: () =>
      drillDownApi.getCategoryProjects({
        time_period: params.timePeriod ?? null,
        category_id: params.categoryId ?? null,
        dept_level: params.deptLevel ?? null,
        dept_name: params.deptName ?? null,
        role: params.role ?? null,
      }),
    enabled: Boolean(params.categoryId),
  });
}

export function useMonthlyPersons(params: {
  month?: string | null;
  deptLevel?: number | null;
  deptName?: string | null;
  role?: string | null;
}) {
  return useQuery({
    queryKey: ["monthly-persons", params],
    queryFn: () =>
      drillDownApi.getMonthlyPersons({
        month: params.month ?? null,
        dept_level: params.deptLevel ?? null,
        dept_name: params.deptName ?? null,
        role: params.role ?? null,
      }),
    enabled: Boolean(params.month),
  });
}

export function useCellPersons(params: {
  timePeriod?: string | null;
  categoryId?: number | null;
  deptLevel?: number | null;
  deptName?: string | null;
  role?: string | null;
}) {
  return useQuery({
    queryKey: ["cell-persons", params],
    queryFn: () =>
      drillDownApi.getCellPersons({
        time_period: params.timePeriod ?? null,
        category_id: params.categoryId ?? null,
        dept_level: params.deptLevel ?? null,
        dept_name: params.deptName ?? null,
        role: params.role ?? null,
      }),
    enabled: Boolean(params.categoryId),
  });
}

// ── 筛选器选项 hook ──

export function useFilterOptions() {
  return useQuery({
    queryKey: ["filter-options"],
    queryFn: filterApi.getOptions,
    staleTime: 5 * 60 * 1000,
  });
}
