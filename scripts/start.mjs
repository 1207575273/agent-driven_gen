#!/usr/bin/env node
// 生产启动: 只起后端一个进程(不 reload), 由 FastAPI 同时托管前端静态资源与 API。
// 端口: 环境变量 PORT 优先, 否则用 ports.json 的 backend[0](生产端口固定, 不探测)。

import { spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cfg = JSON.parse(readFileSync(path.join(ROOT, "ports.json"), "utf8"));
const port = Number(process.env.PORT) || cfg.backend[0];

const staticDir = path.join(ROOT, "apps", "back", "static");
if (!existsSync(staticDir)) {
	console.error(
		"[start] 未找到前端产物 apps/back/static。请先执行: pnpm build",
	);
	process.exit(1);
}

console.log(
	`[start] 生产模式: http://localhost:${port}  (前端 + API 同源, 单进程)`,
);
// 注意: SQLite 单写, 生产默认单 worker; 真要横向扩并发, 请换 Postgres。
const child = spawn(
	`uv run --directory apps/back uvicorn app.main:app --host 0.0.0.0 --port ${port}`,
	{ cwd: ROOT, stdio: "inherit", shell: true },
);
child.on("exit", (code) => process.exit(code ?? 0));
