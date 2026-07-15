import { create } from "zustand";

// Zustand 轻量全局 UI 状态示例(与服务端数据分离, 服务端数据交给 React Query)。
interface UiState {
  lastMessage: string | null;
  setLastMessage: (message: string | null) => void;
}

export const useUiStore = create<UiState>()((set) => ({
  lastMessage: null,
  setLastMessage: (lastMessage) => set({ lastMessage }),
}));
