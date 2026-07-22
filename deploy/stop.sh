#!/usr/bin/env bash
# stop.sh —— 杀掉本项目占用的服务进程(dev / 生产均可)
#
# 读 ports.json 的所有端口, 找到占用进程并杀掉。
# 适用: 终端被关 / Ctrl+C 没杀干净 / 端口被残留进程占用。
#
# 用法: ./deploy/stop.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 从 ports.json 读所有端口(node 解析, 项目本就依赖 node)
mapfile -t ports < <(node -e "
const cfg = JSON.parse(require('fs').readFileSync('$ROOT/ports.json', 'utf8'));
[...cfg.backend, ...cfg.frontend].forEach(p => console.log(p));
")

killed=0

for port in "${ports[@]}"; do
  # 优先用 lsof(macOS / Linux), 回退 netstat(Windows Git Bash)
  if command -v lsof &>/dev/null; then
    pids=$(lsof -ti :"$port" 2>/dev/null || true)
  else
    # Windows: netstat 输出 ... LISTENING  <PID>
    pids=$(netstat -ano 2>/dev/null \
           | grep ":${port} " \
           | grep -i LISTENING \
           | awk '{print $NF}' \
           | sort -u || true)
  fi

  for pid in $pids; do
    [[ -z "$pid" ]] && continue
    if command -v lsof &>/dev/null; then
      kill "$pid" 2>/dev/null || true
    else
      # Git Bash 里 taskkill 的 / 要写 //
      taskkill //F //PID "$pid" 2>/dev/null || true
    fi
    echo "[STOP] 端口 $port -> PID $pid 已杀"
    ((killed++)) || true
  done
done

if [[ "$killed" -eq 0 ]]; then
  echo "[STOP] 没有发现运行中的服务进程"
else
  echo "[STOP] 共杀掉 $killed 个进程"
fi
