import { useQuery } from "@tanstack/react-query";
import { type FilterParams, dashboardApi } from "../api/capacity";

export function useDashboardSummary(filters?: FilterParams) {
  return useQuery({
    queryKey: ["dashboard", "summary", filters],
    queryFn: () => dashboardApi.summary(filters),
  });
}

export function useDashboardMonthlyTrend(filters?: FilterParams) {
  return useQuery({
    queryKey: ["dashboard", "monthly-trend", filters],
    queryFn: () => dashboardApi.monthlyTrend(filters),
  });
}
