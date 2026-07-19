"""筛选器服务: 返回所有可选筛选维度值(时间范围、部门、角色、分类)。"""

from collections.abc import Sequence

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.project_category_repository import ProjectCategoryRepository


def _list2seq(items: Sequence[str]) -> list[str]:
    return [str(item) for item in items]


class FilterService:
    """筛选器选项服务: 返回前端筛选项的数据来源。"""

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        category_repo: ProjectCategoryRepository,
    ) -> None:
        self._emp_repo = employee_repo
        self._cat_repo = category_repo

    async def get_options(self) -> dict[str, object]:
        """获取所有筛选维度可选项。"""
        # 时间范围
        time_range: dict[str, object] = {
            "min_month": "2026-01",
            "max_month": "2026-06",
            "available_quarters": ["2026-Q1", "2026-Q2"],
            "available_halfs": ["2026-H1"],
        }

        # 部门
        departments: dict[str, list[str]] = {
            "level1": _list2seq(await self._emp_repo.list_departments(1)),
            "level2": _list2seq(await self._emp_repo.list_departments(2)),
            "level3": _list2seq(await self._emp_repo.list_departments(3)),
            "level4": _list2seq(await self._emp_repo.list_departments(4)),
        }

        # 角色
        roles = _list2seq(await self._emp_repo.list_roles())

        # 项目分类(树形)
        majors = await self._cat_repo.get_major_categories()
        categories: dict[str, object] = {  # type: ignore[assignment]
            "level1": majors,
        }

        return {
            "time_range": time_range,
            "departments": departments,
            "roles": roles,
            "categories": categories,
        }
