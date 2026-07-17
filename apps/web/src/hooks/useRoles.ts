import { useQuery } from "@tanstack/react-query";
import { type FilterParams, rolesApi } from "../api/capacity";

export function useRoleAggregation(filters?: FilterParams) {
  return useQuery({
    queryKey: ["roles", "aggregation", filters],
    queryFn: () => rolesApi.aggregation(filters),
  });
}

export function useRoleStructure(filters?: FilterParams) {
  return useQuery({
    queryKey: ["roles", "structure", filters],
    queryFn: () => rolesApi.structure(filters),
  });
}
