import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ItemUpdate, itemsApi, systemApi } from "../api/client";

// 分页列表查询: queryKey 带 limit/offset, keepPreviousData 让翻页不闪空白。
export function useItemsQuery(limit: number, offset: number) {
  return useQuery({
    queryKey: ["items", limit, offset],
    queryFn: () => itemsApi.list({ limit, offset }),
    placeholderData: keepPreviousData,
  });
}

// 写操作: 成功后失效所有分页缓存(["items"] 前缀)以刷新当前页。
export function useItemMutations() {
  const queryClient = useQueryClient();
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["items"] });
  };

  const create = useMutation({ mutationFn: itemsApi.create, onSuccess: invalidate });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: ItemUpdate }) =>
      itemsApi.update(id, payload),
    onSuccess: invalidate,
  });
  const remove = useMutation({ mutationFn: itemsApi.remove, onSuccess: invalidate });

  return { create, update, remove };
}

// 后端在线探测: 每 15s 轮询一次 /health, 给页面一个真实的"在线"指示。
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: systemApi.health,
    retry: false,
    refetchInterval: 15000,
  });
}

// 主机资源(CPU / 内存)轮询: 每 2s 拉一次, 供右上角资源卡片实时刷新。
export function useSystemStats() {
  return useQuery({
    queryKey: ["system-stats"],
    queryFn: systemApi.stats,
    retry: false,
    refetchInterval: 2000,
  });
}
