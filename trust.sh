#!/usr/bin/env sh
# 一键信任本项目 (macOS / Linux / Git Bash)。
# 真正的逻辑在 scripts/trust.mjs, 本脚本只负责: 检测 node、定位项目根、转交执行。
set -eu

# 切到脚本所在目录(= 项目根), 保证无论从哪个工作目录执行都能找到 scripts/trust.mjs。
DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "[FAIL] 未找到 node, 请先安装 Node.js 并加入 PATH 后重试。"
  exit 1
fi

node "$DIR/scripts/trust.mjs"
