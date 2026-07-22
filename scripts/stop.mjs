#!/usr/bin/env node
// 杀掉本项目占用的所有端口进程(dev / 生产均可)。
// 读 ports.json 的全部候选端口, 找到占用 PID 并杀掉。
// 适用: 终端被关 / Ctrl+C 没杀干净 / 端口被残留进程占用。
// 纯 Node 内置模块, 跨平台。用法: pnpm stop

import { execSync, spawn } from "node:child_process";
import { readFileSync } from "node:fs";
import { platform } from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const isWin = platform() === "win32";
const cfg = JSON.parse(readFileSync(path.join(ROOT, "ports.json"), "utf8"));
const ports = [...cfg.backend, ...cfg.frontend];

/** @param {number} port */
function getPidsByPort(port) {
  try {
    if (isWin) {
      // netstat -ano 输出最后一列是 PID, 筛 LISTENING 行
      const out = execSync(`netstat -ano`, { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] });
      const pids = new Set();
      for (const line of out.split("\n")) {
        if (line.includes(`:${port} `) && line.includes("LISTENING")) {
          const pid = line.trim().split(/\s+/).pop();
          if (pid && /^\d+$/.test(pid)) pids.add(pid);
        }
      }
      return [...pids];
    }
    // macOS / Linux: lsof -ti 直接返回 PID
    const out = execSync(`lsof -ti :${port}`, { encoding: "utf8", stdio: ["pipe", "pipe", "ignore"] });
    return out.trim().split("\n").filter(Boolean);
  } catch {
    return [];
  }
}

/** @param {string} pid */
function killPid(pid) {
  if (isWin) {
    spawn("taskkill", ["/F", "/T", "/PID", pid], { stdio: "ignore" });
  } else {
    try {
      process.kill(Number(pid), "SIGTERM");
    } catch {
      // 进程可能已退出
    }
  }
}

let killed = 0;
for (const port of ports) {
  const pids = getPidsByPort(port);
  for (const pid of pids) {
    killPid(pid);
    console.log(`[stop] 端口 ${port} -> PID ${pid} 已杀`);
    killed++;
  }
}

if (killed === 0) {
  console.log("[stop] 没有发现运行中的服务进程");
} else {
  console.log(`[stop] 共杀掉 ${killed} 个进程`);
}
