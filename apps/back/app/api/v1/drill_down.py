"""数据穿透路由(薄控制器): 工时明细记录、部门子节点、分类项目列表。"""

from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import DrillDownServiceDep

router = APIRouter(prefix="/drill-down", tags=["drill-down"])


@router.get("/records")
async def get_records(
    service: DrillDownServiceDep,
    employee_id: int | None = Query(default=None, description="员工 ID(至少提供一个筛选条件)"),
    project_name: str | None = Query(default=None, description="项目名"),
    time_period: str | None = Query(default=None, description="时间范围"),
    category_id: int | None = Query(default=None, description="分类ID"),
    dept_path: str | None = Query(default=None, description="部门路径"),
    limit: int = Query(default=500, description="返回记录上限"),
) -> list[dict[str, Any]]:
    return await service.get_records(
        employee_id=employee_id,
        project_name=project_name,
        time_period=time_period,
        category_id=category_id,
        dept_path=dept_path,
        limit=limit,
    )


@router.get("/dept-children")
async def get_dept_children(
    service: DrillDownServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    parent_dept: str = Query(..., description="上级部门名称(必需)"),
    dept_level: int = Query(..., description="当前层级 1/2/3"),
) -> list[dict[str, Any]]:
    return await service.get_dept_children(
        time_period=time_period,
        parent_dept=parent_dept,
        dept_level=dept_level,
    )


@router.get("/category-projects")
async def get_category_projects(
    service: DrillDownServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    category_id: int = Query(..., description="分类ID(必需)"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
) -> list[dict[str, Any]]:
    return await service.get_category_projects(
        time_period=time_period,
        category_id=category_id,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
    )
