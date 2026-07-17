"""仪表盘路由(薄控制器): 只收参、返 DTO。

首页 KPI 概览 + 月度趋势。
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import DashboardServiceDep
from app.services.filters import QueryFilters

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(
    service: DashboardServiceDep,
    start_date: Annotated[date | None, Query(description="开始日期(YYYY-MM-DD)")] = None,
    end_date: Annotated[date | None, Query(description="结束日期(YYYY-MM-DD)")] = None,
    department: Annotated[str | None, Query(description="部门名称")] = None,
    department_level: Annotated[int, Query(ge=2, le=3, description="部门层级(2=二级, 3=三级)")] = 2,
    role: Annotated[str | None, Query(description="角色")] = None,
    personnel_type: Annotated[str | None, Query(description="人员类型: 在编/外部人力资源")] = None,
) -> dict[str, Any]:
    """顶部 4 卡片: 总人天/填报人数/项目数/部门数。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
        role=role,
        personnel_type=personnel_type,
    )
    return await service.get_summary(filters)


@router.get("/monthly-trend")
async def dashboard_monthly_trend(
    service: DashboardServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    department_level: Annotated[int, Query(ge=2, le=3)] = 2,
    role: Annotated[str | None, Query()] = None,
    personnel_type: Annotated[str | None, Query()] = None,
    project: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    """月度总人天趋势折线图。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
        role=role,
        personnel_type=personnel_type,
        project_name=project,
    )
    return await service.get_monthly_trend(filters)
