#!/usr/bin/env bash
# 傻瓜一键起: 装依赖 -> pnpm dev(自动探测端口, 起后端 + 前端)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[INFO] 安装后端依赖 (uv sync)..."
uv sync --directory "$ROOT/apps/back"

echo "[INFO] 安装前端依赖 (pnpm install)..."
(cd "$ROOT" && pnpm install)

echo "[INFO] 启动 (端口见 ports.json, 自动探测空闲端口)..."
(cd "$ROOT" && pnpm dev)
