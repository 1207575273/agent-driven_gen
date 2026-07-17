"""筛选器路由(薄控制器): 提供前端下拉框选项数据。"""

from typing import Any

from fastapi import APIRouter

from app.api.deps import FilterServiceDep

router = APIRouter(prefix="/filters", tags=["filters"])


@router.get("/options")
async def filter_options(service: FilterServiceDep) -> dict[str, Any]:
    """返回所有可用筛选维度值(供前端下拉框)。"""
    return await service.get_filter_options()
