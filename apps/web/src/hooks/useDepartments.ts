import { useQuery } from "@tanstack/react-query";
import { type FilterParams, departmentsApi } from "../api/capacity";

export function useDepartmentOverview(filters?: FilterParams) {
  return useQuery({
    queryKey: ["departments", "overview", filters],
    queryFn: () => departmentsApi.overview(filters),
    enabled: Boolean(filters?.department),
  });
}

export function useDepartmentMembers(filters?: FilterParams) {
  return useQuery({
    queryKey: ["departments", "members", filters],
    queryFn: () => departmentsApi.members(filters),
    enabled: Boolean(filters?.department),
  });
}

export function useMemberProjects(employeeId: number | null, filters?: FilterParams) {
  return useQuery({
    queryKey: ["departments", "member-projects", employeeId, filters],
    queryFn: () => {
      if (employeeId === null) return Promise.resolve([]);
      return departmentsApi.memberProjects(employeeId, filters);
    },
    enabled: employeeId !== null,
  });
}
