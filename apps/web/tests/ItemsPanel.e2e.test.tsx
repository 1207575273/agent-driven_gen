import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Item } from "../src/api/client";
import { ItemsPanel } from "../src/components/ItemsPanel";

// echarts 在 jsdom 下渲染无意义且重, 用空组件替身, 只测交互与契约。
vi.mock("../src/components/QuantityChart", () => ({ QuantityChart: () => null }));

// 交互级端到端: 走真实 api/client.ts, 用 mock fetch 当后端, 锁死前后端 HTTP 契约
// (列表分页 URL、新增、更新的路径与信封结构)。既是契约护栏, 也补 ItemsPanel 交互覆盖。
// 说明: 这是 jsdom 层的端到端, 锁的是"前端对契约的假设"; 后端字段漂移仍靠后端集成测试守,
// 需要真实跨栈护栏时再加可选的浏览器 E2E(见 docs, 不进硬闸门)。

type FakeItem = Item;

let store: FakeItem[] = [];
let fetchMock: ReturnType<typeof vi.fn>;

function jsonResponse(data: unknown): Response {
  return {
    ok: true,
    status: 200,
    json: async () => data,
    text: async () => "",
  } as unknown as Response;
}

function makeItem(id: number, name: string, quantity = 0): FakeItem {
  return {
    id,
    name,
    description: null,
    quantity,
    created_at: "2026-07-20T00:00:00Z",
    updated_at: "2026-07-20T00:00:00Z",
  };
}

function fakeBackend(input: string, init?: RequestInit): Response {
  const url = new URL(input, "http://localhost");
  const method = init?.method ?? "GET";
  const path = url.pathname.replace("/api/v1", "");

  if (path === "/health") {
    return jsonResponse({ status: "ok" });
  }
  if (path === "/items" && method === "GET") {
    const limit = Number(url.searchParams.get("limit"));
    const offset = Number(url.searchParams.get("offset"));
    return jsonResponse({
      items: store.slice(offset, offset + limit),
      total: store.length,
      limit,
      offset,
    });
  }
  if (path === "/items" && method === "POST") {
    const body = JSON.parse(String(init?.body)) as { name: string; quantity?: number };
    const created = makeItem(store.length + 1, body.name, body.quantity ?? 0);
    store.push(created);
    return jsonResponse(created);
  }
  const updateMatch = path.match(/^\/items\/(\d+)\/update$/);
  if (updateMatch && method === "POST") {
    const id = Number(updateMatch[1]);
    const body = JSON.parse(String(init?.body)) as Partial<FakeItem>;
    const target = store.find((it) => it.id === id);
    if (target) {
      Object.assign(target, body);
    }
    return jsonResponse(target);
  }
  throw new Error(`unhandled fetch: ${method} ${path}`);
}

function renderPanel(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

beforeEach(() => {
  store = [makeItem(1, "种子条目", 2)];
  fetchMock = vi.fn((input: string, init?: RequestInit) =>
    Promise.resolve(fakeBackend(input, init)),
  );
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("ItemsPanel 端到端契约", () => {
  it("should load list via GET /items with limit and offset", async () => {
    renderPanel(<ItemsPanel />);

    expect(await screen.findByText("种子条目")).toBeInTheDocument();
    // 锁列表契约: GET /api/v1/items?limit=8&offset=0(PAGE_SIZE=8)
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/items?limit=8&offset=0",
      expect.objectContaining({ headers: expect.any(Object) }),
    );
  });

  it("should create an item end-to-end then show it in the list", async () => {
    renderPanel(<ItemsPanel />);
    await screen.findByText("种子条目");

    fireEvent.change(screen.getByLabelText("名称"), { target: { value: "新条目" } });
    fireEvent.click(screen.getByRole("button", { name: "创建" }));

    // 新增后列表刷新, 新条目出现
    expect(await screen.findByText("新条目")).toBeInTheDocument();
    // 锁新增契约: POST /api/v1/items, body 带 name
    const createCall = fetchMock.mock.calls.find(
      ([u, i]) => u === "/api/v1/items" && i?.method === "POST",
    );
    expect(createCall).toBeDefined();
    expect(JSON.parse(String(createCall?.[1]?.body))).toMatchObject({ name: "新条目" });
  });

  it("should increment quantity via POST /items/{id}/update", async () => {
    renderPanel(<ItemsPanel />);
    await screen.findByText("种子条目"); // 单条种子数据, 页面上只有一个"增加"按钮

    fireEvent.click(screen.getByRole("button", { name: "增加" }));

    // 锁更新契约: POST /api/v1/items/1/update, body 带新 quantity
    await waitFor(() => {
      const updateCall = fetchMock.mock.calls.find(
        ([u, i]) => u === "/api/v1/items/1/update" && i?.method === "POST",
      );
      expect(updateCall).toBeDefined();
      expect(JSON.parse(String(updateCall?.[1]?.body))).toMatchObject({ quantity: 3 });
    });
  });
});
