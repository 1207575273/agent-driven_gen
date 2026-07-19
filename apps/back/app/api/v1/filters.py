"""筛选器选项路由(薄控制器): 返回时间/部门/角色/分类可选值。"""

from typing import Any

from fastapi import APIRouter

from app.api.deps import FilterServiceDep

router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("/options")
async def get_filter_options(service: FilterServiceDep) -> dict[str, Any]:
    return await service.get_options()
