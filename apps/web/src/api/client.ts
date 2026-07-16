// 轻量 API 客户端: 只用 GET / POST, 与后端约定一致。
// 想要强类型可跑 `pnpm gen:api` 用 openapi-typescript 生成 schema, 但不强制。

const BASE = "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    throw new Error(`API ${resp.status}: ${await resp.text()}`);
  }
  return (await resp.json()) as T;
}

export interface Item {
  id: number;
  name: string;
  description: string | null;
  quantity: number;
  created_at: string;
  updated_at: string;
}

export interface ItemCreate {
  name: string;
  description?: string;
  quantity?: number;
}

export interface ItemUpdate {
  name?: string;
  description?: string;
  quantity?: number;
}

// 更新/删除走 POST 子路径, 不用 PATCH/PUT/DELETE。
export const itemsApi = {
  list: () => request<Item[]>("/items"),
  create: (payload: ItemCreate) =>
    request<Item>("/items", { method: "POST", body: JSON.stringify(payload) }),
  update: (id: number, payload: ItemUpdate) =>
    request<Item>(`/items/${id}/update`, { method: "POST", body: JSON.stringify(payload) }),
  remove: (id: number) => request<{ success: boolean }>(`/items/${id}/delete`, { method: "POST" }),
};

export interface SystemStats {
  cpu_percent: number; // 本进程占整机 CPU 的百分比
  mem_rss: number; // 本进程常驻内存(字节)
  mem_percent: number; // 本进程占系统内存的百分比
  mem_total: number; // 系统总内存(字节)
}

export const systemApi = {
  health: () => request<{ status: string }>("/health"),
  stats: () => request<SystemStats>("/system/stats"),
};
