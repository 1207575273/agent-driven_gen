"""角色服务层: 角色维度分析业务逻辑。

不碰 session/SQL, 依赖 WorkHourRepository。
"""

from typing import Any

from app.repositories.work_hour_repository import WorkHourRepository
from app.services.filters import QueryFilters


class RoleService:
    def __init__(self, wh_repo: WorkHourRepository) -> None:
        self._wh_repo = wh_repo

    async def get_aggregation(self, filters: QueryFilters) -> list[dict[str, Any]]:
        """按角色聚合: 各角色总人天 + 部门分布。"""
        role_rows = await self._wh_repo.aggregate_by_role(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
        )

        result: list[dict[str, Any]] = []
        for row in role_rows:
            role_name, total_days, person_count = row

            dept_dist_rows = await self._wh_repo.aggregate_role_dept_distribution(
                role=role_name,
                start_date=filters.start_date,
                end_date=filters.end_date,
                department=filters.department,
                department_level=filters.department_level,
            )

            dept_distribution = [
                {
                    "department": d[0],
                    "person_count": d[1],
                    "total_days": round(d[2], 1),
                }
                for d in dept_dist_rows
            ]

            result.append(
                {
                    "role": role_name,
                    "total_days": round(total_days, 1),
                    "person_count": person_count,
                    "dept_distribution": dept_distribution,
                }
            )

        return result

    async def get_structure(self, filters: QueryFilters) -> list[dict[str, Any]]:
        """人力结构: 按员工状态分组统计(饼图数据)。"""
        rows = await self._wh_repo.aggregate_by_status(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
        )

        total_days_all = sum(r[1] for r in rows)

        return [
            {
                "employee_status": row[0],
                "total_days": round(row[1], 1),
                "person_count": row[2],
                "percentage": round(row[1] / total_days_all * 100, 1) if total_days_all > 0 else 0,
            }
            for row in rows
        ]
