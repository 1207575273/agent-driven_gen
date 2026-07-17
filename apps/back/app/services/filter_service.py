"""筛选器服务层: 提供前端下拉框选项数据。

不碰 session/SQL, 依赖 EmployeeRepository + WorkHourRepository。
"""

from datetime import date
from typing import Any

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.work_hour_repository import WorkHourRepository


class FilterService:
    def __init__(self, wh_repo: WorkHourRepository, emp_repo: EmployeeRepository) -> None:
        self._wh_repo = wh_repo
        self._emp_repo = emp_repo

    async def get_filter_options(self) -> dict[str, Any]:
        """返回所有可用筛选维度值。"""
        departments = await self._emp_repo.list_departments(level=2)
        roles = await self._emp_repo.list_roles()
        personnel_types = await self._emp_repo.list_personnel_types()
        employee_statuses = await self._emp_repo.list_employee_statuses()

        project_rows = await self._wh_repo.aggregate_by_project()
        projects = [row[0] for row in project_rows]

        month_rows = await self._wh_repo.aggregate_by_month()
        if month_rows:
            min_month = month_rows[0][0]
            max_month = month_rows[-1][0]
            date_range = {
                "min": f"{min_month}-01",
                "max": f"{max_month}-28",
            }
        else:
            today = date.today()
            date_range = {
                "min": today.replace(day=1).isoformat(),
                "max": today.isoformat(),
            }

        return {
            "departments": departments,
            "roles": roles,
            "personnel_types": personnel_types,
            "employee_statuses": employee_statuses,
            "projects": projects,
            "date_range": date_range,
        }
