import { useQuery } from "@tanstack/react-query";
import { filtersApi } from "../api/capacity";

export function useFilterOptions() {
  return useQuery({
    queryKey: ["filters"],
    queryFn: filtersApi.options,
    staleTime: 5 * 60 * 1000,
  });
}
