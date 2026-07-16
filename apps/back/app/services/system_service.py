"""进程资源指标服务: 报告**当前后端进程**占用的 CPU / 内存(不是整机)。

口径统一为"这个正在跑的进程"(pnpm dev / pnpm start / 直接 uvicorn 都一样,
取 os.getpid() 就是当前应用进程):
- cpu_percent: 本进程 CPU 占用 / 逻辑核数  => 占整机 CPU 的百分比 (0~100)
- mem_rss:     本进程常驻内存 RSS (字节)
- mem_percent: 本进程 RSS / 系统总内存 * 100 => 占系统内存的百分比
- mem_total:   系统总内存 (字节), 仅作分母参考

无数据访问, 三层在此退化为 route -> service, 不设 repository。
"""

import os

import psutil
from pydantic import BaseModel

_PROC = psutil.Process(os.getpid())
_CORES = psutil.cpu_count(logical=True) or 1
# 建立 CPU 基线: 首次 cpu_percent(interval=None) 返回 0, 之后才是自上次以来的真实增量,
# 且非阻塞、不卡事件循环。模块加载时先打一枪。
_PROC.cpu_percent(interval=None)


class ProcessStats(BaseModel):
    """当前进程资源占用快照(出参契约)。"""

    cpu_percent: float  # 本进程占整机 CPU 的百分比 0~100
    mem_rss: int  # 本进程常驻内存 RSS(字节)
    mem_percent: float  # 本进程占系统内存的百分比 0~100
    mem_total: int  # 系统总内存(字节, 分母参考)


class SystemService:
    def stats(self) -> ProcessStats:
        mem = _PROC.memory_info()
        return ProcessStats(
            cpu_percent=round(_PROC.cpu_percent(interval=None) / _CORES, 1),
            mem_rss=int(mem.rss),
            mem_percent=round(float(_PROC.memory_percent()), 2),
            mem_total=int(psutil.virtual_memory().total),
        )
