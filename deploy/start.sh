#!/usr/bin/env bash
# start.sh —— 统一启动入口(dev / 生产)
#
# 用法(Git Bash / macOS / Linux):
#   ./deploy/start.sh           # 默认 dev
#   ./deploy/start.sh dev       # 开发模式(热更新, 自动探测端口)
#   ./deploy/start.sh prod      # 生产模式(先构建前端再起单进程后端)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

mode="${1:-dev}"

case "$mode" in
  dev)
    echo "[START] 开发模式(热更新)"
    # 确保依赖就绪
    pnpm install
    uv sync --directory apps/back
    pnpm dev
    ;;
  prod)
    echo "[START] 生产模式(同源单进程)"
    pnpm build
    pnpm start
    ;;
  *)
    echo "用法: $0 [dev|prod]"
    echo "  dev   开发模式(默认): 热更新, 自动探测端口"
    echo "  prod  生产模式: 先构建前端再起单进程后端(同源托管)"
    exit 1
    ;;
esac
