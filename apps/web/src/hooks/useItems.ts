import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ItemUpdate, itemsApi, systemApi } from "../api/client";

// 服务端数据与 UI 分离: 所有 Item 的读写都收拢在这个 hook, 组件只管渲染。
export function useItems() {
  const queryClient = useQueryClient();
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["items"] });
  };

  const list = useQuery({ queryKey: ["items"], queryFn: itemsApi.list });
  const create = useMutation({ mutationFn: itemsApi.create, onSuccess: invalidate });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: ItemUpdate }) =>
      itemsApi.update(id, payload),
    onSuccess: invalidate,
  });
  const remove = useMutation({ mutationFn: itemsApi.remove, onSuccess: invalidate });

  return { list, create, update, remove };
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
