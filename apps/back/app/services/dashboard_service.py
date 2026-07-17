"""仪表盘服务层: 首页 KPI 概览数据编排。

不碰 session/SQL, 依赖 WorkHourRepository。
"""

from typing import Any

from app.repositories.work_hour_repository import WorkHourRepository
from app.services.filters import QueryFilters


class DashboardService:
    def __init__(self, wh_repo: WorkHourRepository) -> None:
        self._wh_repo = wh_repo

    async def get_summary(self, filters: QueryFilters) -> dict[str, Any]:
        """获取顶部 4 卡片数据: 总人天/填报人数/项目数/部门数。"""
        project_rows = await self._wh_repo.aggregate_by_project(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )

        total_person_days = sum(row[1] for row in project_rows)
        project_count = len(project_rows)

        person_rows = await self._wh_repo.aggregate_by_person(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )
        reporter_count = len(person_rows)

        departments_set: set[str] = set()
        for row in person_rows:
            dept = row[3]
            if dept:
                departments_set.add(dept)
        department_count = len(departments_set)

        return {
            "total_person_days": round(total_person_days, 1),
            "reporter_count": reporter_count,
            "project_count": project_count,
            "department_count": department_count,
        }

    async def get_monthly_trend(self, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取月度总人天趋势。"""
        rows = await self._wh_repo.aggregate_by_month(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
            project_name=filters.project_name,
        )
        return [{"month": row[0], "total_days": round(row[1], 1)} for row in rows]
