import { create } from "zustand";

// 全局筛选状态：影响所有页面的查询。
// 服务端数据走 React Query(queryKey 含筛选值自动 refetch)，纯 UI 筛选状态走 Zustand。
export interface FilterState {
  timeGranularity: "month" | "quarter" | "half";
  timePeriod: string | null;
  deptLevel: number | null;
  deptName: string | null;
  deptPath: string | null;
  role: string | null;
  categoryId: number | null;
  categoryLevel: number;
  setFilter: (key: string, value: string | number | null) => void;
  resetFilters: () => void;
}

const DEFAULTS = {
  timeGranularity: "half" as const,
  timePeriod: "2026-H1",
  deptLevel: 1 as number | null,
  deptName: null as string | null,
  deptPath: null as string | null,
  role: null as string | null,
  categoryId: null as number | null,
  categoryLevel: 1,
};

export const useFilterStore = create<FilterState>()((set) => ({
  ...DEFAULTS,
  setFilter: (key, value) =>
    set((state) => {
      // 当部门名改变时，同步重置 deptPath
      if (key === "deptName" && value !== state.deptName) {
        return {
          [key]: value,
          deptPath: null,
        } as Partial<FilterState>;
      }
      return { [key]: value } as Partial<FilterState>;
    }),
  resetFilters: () => set(DEFAULTS),
}));
