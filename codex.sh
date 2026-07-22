#!/usr/bin/env bash
# codex.sh —— 在 Git Bash 里启动 Codex(可选)
#
# Windows 原生 Codex 默认用 PowerShell 执行命令。本脚本设好 SHELL 环境变量,
# 让 Codex 尝试用 Git Bash(与项目里的 .sh 脚本、UTF-8、Unix 语法对齐)。
# 若 Codex 不认这个变量,至少从 Git Bash 启动后它会继承当前 shell。
#
# 用法(在 Git Bash 里):
#   ./codex.sh                   # 启动交互式会话
#   ./codex.sh "帮我检查后端"     # 带初始 prompt
#   ./codex.sh -s workspace-write --ask-for-approval on-request
#
# 不想用就直接 `codex`,没有副作用。

set -euo pipefail

# 探测 Git Bash 路径(不写死,适配不同安装位置)
for candidate in \
  "/c/Program Files/Git/bin/bash.exe" \
  "/d/Program Files/Git/bin/bash.exe" \
  "$(command -v bash 2>/dev/null)"; do
  if [[ -n "${candidate:-}" && -x "${candidate}" ]]; then
    export SHELL="${candidate}"
    break
  fi
done

exec codex "$@"
