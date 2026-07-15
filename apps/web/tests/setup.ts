import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// vitest 未开 globals, 需显式注册每个测试后的 DOM 清理, 避免渲染残留互相污染。
afterEach(() => {
  cleanup();
});
