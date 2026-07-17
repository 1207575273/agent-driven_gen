"""部门路由(薄控制器): 部门/团队看板。

部门概况、人员排行榜(含偏离度)、人员下钻。
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import DepartmentServiceDep
from app.services.filters import QueryFilters

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("/overview")
async def department_overview(
    service: DepartmentServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str, Query(description="部门名称(必需)")] = "",
    level: Annotated[int, Query(ge=2, le=3, description="部门层级(默认二级)")] = 2,
) -> dict[str, Any]:
    """部门概况: 总人天/人均人天/项目分布饼图/集中度。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department if department else None,
        department_level=level,
    )
    return await service.get_overview(filters)


@router.get("/members")
async def department_members(
    service: DepartmentServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str, Query(description="部门名称(必需)")] = "",
    level: Annotated[int, Query(ge=2, le=3)] = 2,
    role: Annotated[str | None, Query()] = None,
    personnel_type: Annotated[str | None, Query()] = None,
) -> list[dict[str, Any]]:
    """人员投入排行榜(含偏离度)。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department if department else None,
        department_level=level,
        role=role,
        personnel_type=personnel_type,
    )
    return await service.get_members(filters)


@router.get("/members/{employee_id}/projects")
async def member_projects(
    employee_id: int,
    service: DepartmentServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> list[dict[str, Any]]:
    """某人下钻: 项目投入明细 + 月度分布。"""
    filters = QueryFilters(start_date=start_date, end_date=end_date)
    return await service.get_member_projects(employee_id, filters)
