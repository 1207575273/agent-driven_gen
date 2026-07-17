import { useQuery } from "@tanstack/react-query";
import { type FilterParams, projectsApi } from "../api/capacity";

export function useProjectRanking(filters?: FilterParams) {
  return useQuery({
    queryKey: ["projects", "ranking", filters],
    queryFn: () => projectsApi.ranking(filters),
  });
}

export function useProjectMembers(projectName: string | null, filters?: FilterParams) {
  return useQuery({
    queryKey: ["projects", "members", projectName, filters],
    queryFn: () => {
      if (!projectName) return Promise.resolve([]);
      return projectsApi.members(projectName, filters);
    },
    enabled: Boolean(projectName),
  });
}

export function useProjectMonthlyTrend(projectName: string | null, filters?: FilterParams) {
  return useQuery({
    queryKey: ["projects", "monthly-trend", projectName, filters],
    queryFn: () => {
      if (!projectName) return Promise.resolve([]);
      return projectsApi.monthlyTrend(projectName, filters);
    },
    enabled: Boolean(projectName),
  });
}
