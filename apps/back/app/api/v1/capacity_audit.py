"""产能填报审计路由(薄控制器): 只收 query params, 调 service, 返 DTO。"""

from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import CapacityAuditServiceDep

router = APIRouter(prefix="/capacity-audit", tags=["capacity-audit"])


@router.get("/summary")
async def get_summary(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="2026-H1 / 2026-Q1 / 2026-01"),
    dept_level: int | None = Query(default=None, description="部门层级 1-4"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
) -> dict[str, Any]:
    return await service.get_summary(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
    )


@router.get("/monthly-trend")
async def get_monthly_trend(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="2026-H1 / 2026-Q1 / 2026-01"),
    dept_level: int | None = Query(default=None, description="部门层级 1-4"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
) -> list[dict[str, Any]]:
    return await service.get_monthly_trend(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
    )


@router.get("/department-fill-rate")
async def get_department_fill_rate(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int = Query(default=2, description="部门层级"),
    parent_dept: str | None = Query(default=None, description="上级部门名称(下钻时传入)"),
    role: str | None = Query(default=None, description="角色筛选"),
) -> list[dict[str, Any]]:
    return await service.get_department_fill_rate(
        time_period=time_period,
        dept_level=dept_level,
        parent_dept=parent_dept,
        role=role,
    )


@router.get("/zero-filling")
async def get_zero_filling(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
) -> list[dict[str, Any]]:
    return await service.get_zero_filling(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
    )


@router.get("/deviation-ranking")
async def get_deviation_ranking(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
    deviation_direction: str = Query(default="all", description="positive/negative/all"),
    sort_by: str = Query(default="deviation_abs", description="排序字段"),
    sort_dir: str = Query(default="desc", description="asc/desc"),
    is_abnormal_only: bool = Query(default=False, description="仅显示异常"),
) -> list[dict[str, Any]]:
    return await service.get_deviation_ranking(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        deviation_direction=deviation_direction,
        sort_by=sort_by,
        sort_dir=sort_dir,
        is_abnormal_only=is_abnormal_only,
    )


@router.get("/abnormal-detail")
async def get_abnormal_detail(
    service: CapacityAuditServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
) -> list[dict[str, Any]]:
    return await service.get_abnormal_detail(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
    )


@router.get("/person-monthly")
async def get_person_monthly(
    service: CapacityAuditServiceDep,
    employee_id: int = Query(..., description="员工 ID"),
) -> dict[str, Any]:
    return await service.get_person_monthly(employee_id)


@router.get("/person-projects")
async def get_person_projects(
    service: CapacityAuditServiceDep,
    employee_id: int = Query(..., description="员工 ID"),
    time_period: str | None = Query(default=None, description="时间范围"),
) -> list[dict[str, Any]]:
    return await service.get_person_projects(
        employee_id=employee_id,
        time_period=time_period,
    )
