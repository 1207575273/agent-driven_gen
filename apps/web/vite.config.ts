import { readFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// 端口优先用 dev 编排脚本(scripts/dev.mjs)通过 env 注入; 单独起前端时回退 ports.json 首个候选。
const here = path.dirname(fileURLToPath(import.meta.url));
const ports = JSON.parse(readFileSync(path.resolve(here, "../../ports.json"), "utf8"));
const frontendPort = Number(process.env.FRONTEND_PORT) || ports.frontend[0];
const backendPort = Number(process.env.BACKEND_PORT) || ports.backend[0];

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: frontendPort,
    // 端口已由 dev.mjs 探测确保空闲, 固定用它, 不再自动跳
    strictPort: true,
    proxy: {
      "/api": `http://localhost:${backendPort}`,
    },
  },
  build: {
    // 构建产物输出到后端 static 目录, 由 FastAPI 一并托管。
    outDir: "../back/static",
    emptyOutDir: true,
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
  },
});
