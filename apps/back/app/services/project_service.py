"""项目服务层: 项目投入看板业务逻辑。

不碰 session/SQL, 依赖 WorkHourRepository。
"""

from typing import Any

from app.repositories.work_hour_repository import WorkHourRepository
from app.services.filters import QueryFilters


class ProjectService:
    def __init__(self, wh_repo: WorkHourRepository) -> None:
        self._wh_repo = wh_repo

    async def get_ranking(self, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取项目投入人天排行榜。"""
        rows = await self._wh_repo.aggregate_by_project(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )
        return [
            {
                "project_name": row[0],
                "total_days": round(row[1], 1),
                "member_count": row[2],
                "avg_days_per_person": round(row[1] / row[2], 1) if row[2] > 0 else 0,
                "concentration": round(row[1] / row[2], 1) if row[2] > 0 else 0,
            }
            for row in rows
        ]

    async def get_project_members(self, project_name: str, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取项目下钻人员投入明细(含月度拆分)。"""
        person_rows = await self._wh_repo.aggregate_by_person(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
            project_name=project_name,
        )

        result: list[dict[str, Any]] = []
        for row in person_rows:
            employee_id = row[0]
            name = row[1]
            role = row[2]
            dept = row[3]
            total_days = row[4]

            monthly_rows = await self._wh_repo.aggregate_person_project_by_month(
                employee_id=employee_id,
                project_name=project_name,
                start_date=filters.start_date,
                end_date=filters.end_date,
            )
            monthly_breakdown = [{"month": m[0], "days": round(m[1], 1)} for m in monthly_rows]

            result.append(
                {
                    "employee_id": employee_id,
                    "name": name,
                    "role": role,
                    "department": dept,
                    "total_days": round(total_days, 1),
                    "monthly_breakdown": monthly_breakdown,
                }
            )

        return result

    async def get_project_monthly_trend(self, project_name: str, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取选定项目月度趋势。"""
        rows = await self._wh_repo.aggregate_by_month(
            start_date=filters.start_date,
            end_date=filters.end_date,
            project_name=project_name,
        )
        return [{"month": row[0], "total_days": round(row[1], 1)} for row in rows]
