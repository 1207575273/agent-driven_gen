#!/usr/bin/env node
// 本地开发编排: 读 ports.json -> 探测空闲端口(冲突检测) -> 起后端 + 前端。
// 纯 Node 内置模块, 零第三方依赖。端口全自动、前端代理自动跟随后端。

import { spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import net from "node:net";
import { platform } from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function isPortFree(port) {
	return new Promise((resolve) => {
		const server = net.createServer();
		server.once("error", () => resolve(false));
		server.once("listening", () => server.close(() => resolve(true)));
		server.listen(port, "127.0.0.1");
	});
}

async function pickPort(label, candidates) {
	for (const port of candidates) {
		if (await isPortFree(port)) {
			return port;
		}
	}
	console.error(
		`[ports] ${label}候选端口 ${candidates.join(", ")} 全部被占用。请释放端口, 或改 ports.json。`,
	);
	process.exit(1);
}

const cfg = JSON.parse(readFileSync(path.join(ROOT, "ports.json"), "utf8"));
const backendPort = await pickPort("后端", cfg.backend);
const frontendPort = await pickPort("前端", cfg.frontend);
console.log(
	`[ports] 后端 -> http://localhost:${backendPort}  前端 -> http://localhost:${frontendPort}`,
);

const children = [];
let shuttingDown = false;

function killChild(child) {
	if (child.killed || child.pid == null) {
		return;
	}
	if (platform() === "win32") {
		// Windows 下需连子进程树一起杀, 否则 uvicorn/vite 会残留
		spawn("taskkill", ["/pid", String(child.pid), "/T", "/F"], {
			stdio: "ignore",
		});
	} else {
		child.kill("SIGINT");
	}
}

function shutdown(code) {
	if (shuttingDown) {
		return;
	}
	shuttingDown = true;
	for (const child of children) {
		killChild(child);
	}
	process.exit(code);
}

function run(command, extraEnv) {
	const child = spawn(command, {
		cwd: ROOT,
		stdio: "inherit",
		shell: true,
		env: { ...process.env, ...extraEnv },
	});
	child.on("exit", (code) => shutdown(code ?? 0));
	children.push(child);
}

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));

run(
	`uv run --directory apps/back uvicorn app.main:app --reload --port ${backendPort}`,
	{},
);
run("pnpm --filter web dev", {
	FRONTEND_PORT: String(frontendPort),
	BACKEND_PORT: String(backendPort),
});
