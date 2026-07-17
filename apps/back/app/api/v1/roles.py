"""角色路由(薄控制器): 角色维度分析。

按角色聚合 + 部门分布 + 人力结构饼图。
"""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Query

from app.api.deps import RoleServiceDep
from app.services.filters import QueryFilters

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/aggregation")
async def role_aggregation(
    service: RoleServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    department_level: Annotated[int, Query(ge=2, le=3)] = 2,
) -> list[dict[str, Any]]:
    """按角色聚合: 各角色总投入及部门分布。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
    )
    return await service.get_aggregation(filters)


@router.get("/structure")
async def role_structure(
    service: RoleServiceDep,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    department_level: Annotated[int, Query(ge=2, le=3)] = 2,
) -> list[dict[str, Any]]:
    """人力结构: 正式/离职/兼岗/实习/顾问/外部 各自人天占比。"""
    filters = QueryFilters(
        start_date=start_date,
        end_date=end_date,
        department=department,
        department_level=department_level,
    )
    return await service.get_structure(filters)
