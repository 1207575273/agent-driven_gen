"""系统资源路由(Controller, 薄): 只读当前进程的 CPU / 内存占用, 用 GET。"""

from fastapi import APIRouter

from app.api.deps import SystemServiceDep
from app.services.system_service import ProcessStats

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/stats", response_model=ProcessStats)
async def system_stats(service: SystemServiceDep) -> ProcessStats:
    return service.stats()
