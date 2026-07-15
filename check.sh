#!/usr/bin/env bash
# 一键质量自查(不拦提交, 想查就跑):
#   后端 Ruff + mypy(strict) + pytest, 前端 Biome + tsc + Vitest。
# 任一不过会以非零码退出, 方便你在合并前自己把关。
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
pnpm check
