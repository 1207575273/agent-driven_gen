"""产能交叉维度分析路由(薄控制器): 时间x分类、部门x分类、角色x分类、人员排名、三快计划。"""

from typing import Any

from fastapi import APIRouter, Query

from app.api.deps import CrossAnalysisServiceDep

router = APIRouter(prefix="/cross-analysis", tags=["cross-analysis"])


@router.get("/time-category")
async def get_time_category(
    service: CrossAnalysisServiceDep,
    time_granularity: str = Query(default="month", description="month/quarter/half"),
    time_period: str | None = Query(default=None, description="2026-H1 / 2026-Q1 等"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
    category_level: int = Query(default=1, description="分类层级 1/2/3"),
    parent_category_id: int | None = Query(default=None, description="上级分类ID(下钻时)"),
) -> list[dict[str, Any]]:
    return await service.get_time_category(
        time_granularity=time_granularity,
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        category_level=category_level,
        parent_category_id=parent_category_id,
    )


@router.get("/should-vs-actual")
async def get_should_vs_actual(
    service: CrossAnalysisServiceDep,
    time_granularity: str = Query(default="month", description="month/quarter/half"),
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
) -> list[dict[str, Any]]:
    return await service.get_should_vs_actual(
        time_granularity=time_granularity,
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
    )


@router.get("/dept-category")
async def get_dept_category(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int = Query(default=2, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称筛选"),
    role: str | None = Query(default=None, description="角色筛选"),
    category_level: int = Query(default=1, description="分类层级"),
    parent_category_id: int | None = Query(default=None, description="上级分类ID(下钻时)"),
) -> list[dict[str, Any]]:
    return await service.get_dept_category(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        category_level=category_level,
        parent_category_id=parent_category_id,
    )


@router.get("/dept-category-matrix")
async def get_dept_category_matrix(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int = Query(default=2, description="部门层级"),
    category_level: int = Query(default=1, description="分类层级"),
) -> dict[str, Any]:
    return await service.get_dept_category_matrix(
        time_period=time_period,
        dept_level=dept_level,
        category_level=category_level,
    )


@router.get("/role-category")
async def get_role_category(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
    category_level: int = Query(default=1, description="分类层级"),
    parent_category_id: int | None = Query(default=None, description="上级分类ID(下钻时)"),
) -> list[dict[str, Any]]:
    return await service.get_role_category(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        category_level=category_level,
        parent_category_id=parent_category_id,
    )


@router.get("/role-monthly-trend")
async def get_role_monthly_trend(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    role: str = Query(..., description="角色(必需)"),
    category_level: int = Query(default=1, description="分类层级"),
) -> list[dict[str, Any]]:
    return await service.get_role_monthly_trend(
        time_period=time_period,
        role=role,
        category_level=category_level,
    )


@router.get("/person-ranking")
async def get_person_ranking(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
    sort_by: str = Query(default="actual_days", description="排序字段"),
    sort_dir: str = Query(default="desc", description="asc/desc"),
) -> list[dict[str, Any]]:
    return await service.get_person_ranking(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/three-fast-comparison")
async def get_three_fast_comparison(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
) -> list[dict[str, Any]]:
    return await service.get_three_fast_comparison(
        time_period=time_period,
    )


@router.get("/person-category")
async def get_person_category(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    dept_level: int | None = Query(default=None, description="部门层级"),
    dept_name: str | None = Query(default=None, description="部门名称"),
    role: str | None = Query(default=None, description="角色筛选"),
    category_level: int = Query(default=1, description="分类层级 1/2/3"),
    parent_category_id: int | None = Query(default=None, description="上级分类ID(下钻时)"),
) -> list[dict[str, Any]]:
    return await service.get_person_category(
        time_period=time_period,
        dept_level=dept_level,
        dept_name=dept_name,
        role=role,
        category_level=category_level,
        parent_category_id=parent_category_id,
    )


@router.get("/matrix")
async def get_matrix(
    service: CrossAnalysisServiceDep,
    time_period: str | None = Query(default=None, description="时间范围"),
    row_dimension: str = Query(default="dept", description="dept/role"),
    col_dimension: str = Query(default="category", description="category"),
    category_level: int = Query(default=1, description="分类层级"),
) -> dict[str, Any]:
    return await service.get_matrix(
        time_period=time_period,
        row_dimension=row_dimension,
        col_dimension=col_dimension,
        category_level=category_level,
    )
