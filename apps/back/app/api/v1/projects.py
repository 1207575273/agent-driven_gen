"""项目路由(薄控制器): 项目投入看板。

排行榜、下钻人员明细、月度趋势。
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import ProjectServiceDep
from app.services.filters import QueryFilters

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/ranking")
async def project_ranking(
    service: ProjectServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    department_level: Annotated[int, Query(ge=2, le=3)] = 2,
    role: Annotated[str | None, Query()] = None,
    personnel_type: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    """项目投入人天排行榜。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
        role=role,
        personnel_type=personnel_type,
    )
    return await service.get_ranking(filters)


@router.get("/{project_name}/members")
async def project_members(
    project_name: str,
    service: ProjectServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    department_level: Annotated[int, Query(ge=2, le=3)] = 2,
    role: Annotated[str | None, Query()] = None,
    personnel_type: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    """项目下钻: 人员投入明细。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
        role=role,
        personnel_type=personnel_type,
    )
    return await service.get_project_members(project_name, filters)


@router.get("/{project_name}/monthly-trend")
async def project_monthly_trend(
    project_name: str,
    service: ProjectServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> list[dict[str, Any]]:
    """选定项目月度趋势。"""
    filters = QueryFilters(start_date=start_date, end_date=end_date)
    return await service.get_project_monthly_trend(project_name, filters)
