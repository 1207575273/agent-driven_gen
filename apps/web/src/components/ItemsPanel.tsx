import { Suspense, lazy, useEffect, useState } from "react";
import type { Item } from "../api/client";
import { useHealth, useItemMutations, useItemsQuery } from "../hooks/useItems";
import { useUiStore } from "../stores/useUiStore";
import { DynamicForm, type FieldConfig, type FormValues } from "./DynamicForm";

// echarts 体积大, 懒加载单独切块, 不拖首屏。
const QuantityChart = lazy(() =>
  import("./QuantityChart").then((m) => ({ default: m.QuantityChart })),
);

const PAGE_SIZE = 8;

const ITEM_FIELDS: FieldConfig[] = [
  {
    name: "name",
    label: "名称",
    type: "text",
    required: true,
    placeholder: "必填",
  },
  { name: "description", label: "描述", type: "text", placeholder: "可选" },
  { name: "quantity", label: "数量", type: "number", placeholder: "0" },
];

function StatusDot() {
  const health = useHealth();
  const map = {
    online: { color: "bg-accent", text: "后端在线" },
    offline: { color: "bg-red-500", text: "后端离线" },
    probing: { color: "bg-neutral-500", text: "探测中…" },
  } as const;
  const state = health.isSuccess ? "online" : health.isError ? "offline" : "probing";
  const { color, text } = map[state];
  return (
    <span className="flex items-center gap-2 text-xs text-neutral-500">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      {text}
    </span>
  );
}

function ItemRow({ item }: { item: Item }) {
  const { update, remove } = useItemMutations();
  const setQuantity = (next: number) => {
    update.mutate({ id: item.id, payload: { quantity: Math.max(0, next) } });
  };
  const updating = update.isPending && update.variables?.id === item.id;
  const removing = remove.isPending && remove.variables === item.id;

  return (
    <div className="flex items-center gap-4 border-t border-neutral-900 px-4 py-3">
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm font-medium text-neutral-100">{item.name}</div>
        {item.description ? (
          <div className="truncate text-xs text-neutral-500">{item.description}</div>
        ) : null}
      </div>

      {/* 数量步进 = 一次 update: POST /items/{id}/update */}
      <div className="flex items-center gap-1">
        <button
          type="button"
          aria-label="减少"
          disabled={updating || item.quantity === 0}
          onClick={() => setQuantity(item.quantity - 1)}
          className="h-7 w-7 rounded-md border border-neutral-700 text-neutral-300 transition hover:border-neutral-500 disabled:opacity-40"
        >
          −
        </button>
        <span className="w-10 text-center font-mono text-sm text-neutral-100">{item.quantity}</span>
        <button
          type="button"
          aria-label="增加"
          disabled={updating}
          onClick={() => setQuantity(item.quantity + 1)}
          className="h-7 w-7 rounded-md border border-neutral-700 text-neutral-300 transition hover:border-neutral-500 disabled:opacity-40"
        >
          +
        </button>
      </div>

      <button
        type="button"
        disabled={removing}
        onClick={() => remove.mutate(item.id)}
        className="rounded-md px-2 py-1 text-xs text-neutral-500 transition hover:bg-red-500/10 hover:text-red-400 disabled:opacity-40"
      >
        {removing ? "删除中…" : "删除"}
      </button>
    </div>
  );
}

export function ItemsPanel() {
  const [offset, setOffset] = useState(0);
  const listQuery = useItemsQuery(PAGE_SIZE, offset);
  const { create } = useItemMutations();
  const lastMessage = useUiStore((s) => s.lastMessage);
  const setLastMessage = useUiStore((s) => s.setLastMessage);
  // 提交成功后换 key 重挂表单以清空输入。
  const [formKey, setFormKey] = useState(0);

  const page = listQuery.data;
  const items = page?.items ?? [];
  const total = page?.total ?? 0;

  // 删除导致本页越界(offset 超过 total)时, 回退到最后一个有效页。
  useEffect(() => {
    if (offset > 0 && offset >= total && total >= 0 && listQuery.isSuccess) {
      setOffset(Math.max(0, (Math.ceil(total / PAGE_SIZE) - 1) * PAGE_SIZE));
    }
  }, [total, offset, listQuery.isSuccess]);

  const handleSubmit = (values: FormValues) => {
    create.mutate(
      {
        name: String(values.name ?? ""),
        description: values.description ? String(values.description) : undefined,
        quantity: values.quantity ? Number(values.quantity) : 0,
      },
      {
        onSuccess: (item) => {
          setLastMessage(`已创建 ${item.name}`);
          setFormKey((k) => k + 1);
        },
      },
    );
  };

  const canPrev = offset > 0;
  const canNext = offset + PAGE_SIZE < total;
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);

  return (
    <section className="py-12">
      <div className="mb-8 flex items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold text-neutral-100">活的示例 · Item CRUD</h2>
          <p className="text-sm text-neutral-500">下面每个动作都真打后端, 全程只用 GET / POST。</p>
        </div>
        <StatusDot />
      </div>

      <div className="rounded-lg border border-neutral-800 bg-neutral-900/40">
        {/* 新增: 配置化动态表单驱动 */}
        <div className="border-b border-neutral-900 p-4">
          <DynamicForm
            key={formKey}
            fields={ITEM_FIELDS}
            onSubmit={handleSubmit}
            submitting={create.isPending}
            submitLabel="创建"
            inline
          />
          {lastMessage ? <p className="mt-3 text-xs text-accent">{lastMessage}</p> : null}
          {create.isError ? (
            <p className="mt-3 text-xs text-red-400">创建失败, 请确认后端已启动。</p>
          ) : null}
        </div>

        <div className="grid grid-cols-1 gap-0 lg:grid-cols-[1fr_340px]">
          {/* 列表 + 分页 */}
          <div className="flex min-w-0 flex-col">
            <div className="flex items-center justify-between px-4 py-3 text-xs text-neutral-500">
              <span>列表 · GET /items?limit&amp;offset</span>
              <span className="font-mono">共 {total} 条</span>
            </div>

            <div className="min-w-0 flex-1">
              {listQuery.isLoading ? (
                <p className="px-4 py-8 text-sm text-neutral-500">加载中…</p>
              ) : listQuery.isError ? (
                <p className="px-4 py-8 text-sm text-red-400">加载失败, 请确认后端已启动。</p>
              ) : items.length === 0 ? (
                <p className="px-4 py-8 text-sm text-neutral-600">
                  还没有数据, 用上面的表单新增一条。
                </p>
              ) : (
                items.map((item) => <ItemRow key={item.id} item={item} />)
              )}
            </div>

            {/* 翻页 */}
            <div className="flex items-center justify-between border-t border-neutral-900 px-4 py-3">
              <span className="font-mono text-xs text-neutral-500">
                {from}–{to} / {total}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={!canPrev}
                  onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                  className="rounded-md border border-neutral-700 px-3 py-1 text-xs text-neutral-300 transition hover:border-neutral-500 disabled:opacity-40"
                >
                  上一页
                </button>
                <button
                  type="button"
                  disabled={!canNext}
                  onClick={() => setOffset(offset + PAGE_SIZE)}
                  className="rounded-md border border-neutral-700 px-3 py-1 text-xs text-neutral-300 transition hover:border-neutral-500 disabled:opacity-40"
                >
                  下一页
                </button>
              </div>
            </div>
          </div>

          {/* 图表: 当前页数据, 实时联动 */}
          <div className="border-t border-neutral-900 p-4 lg:border-t-0 lg:border-l">
            <div className="mb-3 text-xs text-neutral-500">当前页 · 各 Item 数量</div>
            <Suspense
              fallback={
                <div className="flex h-[240px] items-center justify-center text-sm text-neutral-600">
                  图表加载中…
                </div>
              }
            >
              <QuantityChart items={items} />
            </Suspense>
          </div>
        </div>
      </div>
    </section>
  );
}
