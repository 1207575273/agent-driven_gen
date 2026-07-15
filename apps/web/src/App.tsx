import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { itemsApi } from "./api/client";
import { DynamicForm, type FieldConfig, type FormValues } from "./components/DynamicForm";
import { useUiStore } from "./stores/useUiStore";

const ITEM_FIELDS: FieldConfig[] = [
  { name: "name", label: "名称", type: "text", required: true, placeholder: "必填" },
  { name: "description", label: "描述", type: "text", placeholder: "可选" },
  { name: "quantity", label: "数量", type: "number", placeholder: "0" },
];

export function App() {
  const queryClient = useQueryClient();
  const lastMessage = useUiStore((state) => state.lastMessage);
  const setLastMessage = useUiStore((state) => state.setLastMessage);

  const itemsQuery = useQuery({ queryKey: ["items"], queryFn: itemsApi.list });

  const createMutation = useMutation({
    mutationFn: itemsApi.create,
    onSuccess: (item) => {
      setLastMessage(`已创建: ${item.name}`);
      void queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: itemsApi.remove,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["items"] });
    },
  });

  const handleSubmit = (values: FormValues) => {
    createMutation.mutate({
      name: String(values.name ?? ""),
      description: values.description ? String(values.description) : undefined,
      quantity: values.quantity ? Number(values.quantity) : 0,
    });
  };

  return (
    <main style={{ maxWidth: 640, margin: "40px auto", fontFamily: "system-ui, sans-serif" }}>
      <h1>通用母版 · Item 示例</h1>
      <p style={{ color: "#666" }}>
        配置化表单 → POST /api/v1/items → 列表 GET 回显(全程只用 GET / POST)。
      </p>

      <section>
        <h2>新增</h2>
        <DynamicForm
          fields={ITEM_FIELDS}
          onSubmit={handleSubmit}
          submitting={createMutation.isPending}
          submitLabel="创建"
        />
        {lastMessage ? <p style={{ color: "green" }}>{lastMessage}</p> : null}
      </section>

      <section>
        <h2>列表</h2>
        {itemsQuery.isLoading ? <p>加载中...</p> : null}
        {itemsQuery.isError ? (
          <p style={{ color: "crimson" }}>加载失败, 请确认后端已启动。</p>
        ) : null}
        <ul>
          {itemsQuery.data?.map((item) => (
            <li key={item.id}>
              <strong>{item.name}</strong> × {item.quantity}
              {item.description ? ` — ${item.description}` : ""}
              <button
                type="button"
                style={{ marginLeft: 8 }}
                onClick={() => deleteMutation.mutate(item.id)}
              >
                删除
              </button>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
