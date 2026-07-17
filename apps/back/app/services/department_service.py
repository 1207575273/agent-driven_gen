"""部门服务层: 部门/团队看板业务逻辑。

包含偏离度计算和集中度计算。
不碰 session/SQL, 依赖 WorkHourRepository + EmployeeRepository。
"""

from collections.abc import Sequence
from typing import Any

from app.core.exceptions import NotFoundError
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.filters import QueryFilters

# 偏离度等级阈值常量
DEVIATION_NORMAL_THRESHOLD = 0.5
DEVIATION_YELLOW_THRESHOLD = 1.0


class DepartmentService:
    def __init__(self, wh_repo: WorkHourRepository, emp_repo: EmployeeRepository) -> None:
        self._wh_repo = wh_repo
        self._emp_repo = emp_repo

    async def get_overview(self, filters: QueryFilters) -> dict[str, Any]:
        """获取部门概况(总人天/人均人天/项目分布饼图/集中度)。"""
        if not filters.department:
            raise NotFoundError(resource="Department", identifier="未提供部门参数")

        project_rows = await self._wh_repo.aggregate_by_project(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )

        total_person_days = sum(row[1] for row in project_rows)

        person_rows = await self._wh_repo.aggregate_by_person(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )
        member_count = len(person_rows)
        avg_person_days = round(total_person_days / member_count, 1) if member_count > 0 else 0

        project_distribution = [
            {
                "project_name": row[0],
                "total_days": round(row[1], 1),
                "percentage": round(row[1] / total_person_days * 100, 1) if total_person_days > 0 else 0,
            }
            for row in project_rows
        ]

        concentration = self._calculate_concentration(project_rows, total_person_days)

        return {
            "total_person_days": round(total_person_days, 1),
            "avg_person_days": avg_person_days,
            "member_count": member_count,
            "project_distribution": project_distribution,
            "top_n_concentration": concentration,
        }

    async def get_members(self, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取人员投入排行榜(含偏离度)。"""
        if not filters.department:
            raise NotFoundError(resource="Department", identifier="未提供部门参数")

        person_rows = await self._wh_repo.aggregate_by_person(
            start_date=filters.start_date,
            end_date=filters.end_date,
            department=filters.department,
            department_level=filters.department_level,
            role=filters.role,
            personnel_type=filters.personnel_type,
        )

        if not person_rows:
            return []

        deviations = self._calculate_deviations([(row[0], row[1], row[2], row[3], row[4]) for row in person_rows])

        return deviations

    async def get_member_projects(self, employee_id: int, filters: QueryFilters) -> list[dict[str, Any]]:
        """获取某人的项目投入明细 + 月度分布。"""
        employee = await self._emp_repo.get(employee_id)
        if employee is None:
            raise NotFoundError(resource="Employee", identifier=employee_id)

        project_rows = await self._wh_repo.aggregate_by_person_project(
            employee_id=employee_id,
            start_date=filters.start_date,
            end_date=filters.end_date,
        )

        result: list[dict[str, Any]] = []
        for row in project_rows:
            project_name = row[0]
            monthly_rows = await self._wh_repo.aggregate_person_project_by_month(
                employee_id=employee_id,
                project_name=project_name,
                start_date=filters.start_date,
                end_date=filters.end_date,
            )
            monthly_breakdown = [{"month": m[0], "days": round(m[1], 1)} for m in monthly_rows]
            result.append(
                {
                    "project_name": project_name,
                    "total_days": round(row[1], 1),
                    "monthly_breakdown": monthly_breakdown,
                }
            )

        return result

    # ------------------------------------------------------------------
    # 偏离度计算
    # ------------------------------------------------------------------
    def _calculate_deviations(self, person_rows: list[tuple[int, str, str, str, float]]) -> list[dict[str, Any]]:
        """计算偏离度。

        person_rows: [(employee_id, name, role, department, total_days), ...]

        1. 计算同级均值
        2. 对每个人: deviation = (个人人天 - 均值) / 均值
        3. 标记: normal(<=0.5) | yellow(>0.5, <=1.0) | red(>1.0)
        """
        if not person_rows:
            return []

        total = sum(row[4] for row in person_rows)
        peer_avg = total / len(person_rows)

        result: list[dict[str, Any]] = []
        for row in person_rows:
            eid, name, role, dept, days = row
            deviation = (days - peer_avg) / peer_avg if peer_avg > 0 else 0.0

            abs_dev = abs(deviation)
            if abs_dev <= DEVIATION_NORMAL_THRESHOLD:
                deviation_level = "normal"
            elif abs_dev <= DEVIATION_YELLOW_THRESHOLD:
                deviation_level = "yellow"
            else:
                deviation_level = "red"

            result.append(
                {
                    "employee_id": eid,
                    "name": name,
                    "role": role,
                    "department": dept,
                    "total_days": round(days, 1),
                    "peer_avg_days": round(peer_avg, 1),
                    "deviation": round(deviation, 2),
                    "deviation_level": deviation_level,
                }
            )

        return result

    # ------------------------------------------------------------------
    # 集中度计算
    # ------------------------------------------------------------------
    def _calculate_concentration(
        self, project_rows: Sequence[tuple[str, float, int]], total_days: float
    ) -> dict[str, Any]:
        """计算部门投入集中度: Top 3 和 Top 5 项目人天占比。"""
        if total_days <= 0:
            return {"top3_percentage": 0, "top5_percentage": 0}

        sorted_rows = sorted(project_rows, key=lambda r: r[1], reverse=True)

        top3_sum = sum(r[1] for r in sorted_rows[:3])
        top5_sum = sum(r[1] for r in sorted_rows[:5])

        return {
            "top3_percentage": round(top3_sum / total_days * 100, 1),
            "top5_percentage": round(top5_sum / total_days * 100, 1),
        }
