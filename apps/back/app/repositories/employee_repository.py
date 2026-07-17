"""Employee 仓储层(Repository / DAO): 封装花名册数据的查询。

持有 AsyncSession, 只做数据访问, 不包含业务逻辑。
"""

from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_departments(self, level: int = 2) -> list[str]:
        """获取部门列表(distinct level2 或 level3 部门)。"""
        dept_col = getattr(Employee, f"level{level}_dept")
        query = select(dept_col).where(dept_col.isnot(None)).where(dept_col != "").distinct().order_by(dept_col)
        result = await self._session.exec(query)
        rows = result.all()
        return [str(r) for r in rows if r]

    async def list_roles(self) -> list[str]:
        """获取角色列表(distinct)。"""
        query = (
            select(Employee.role)
            .where(col(Employee.role).isnot(None))
            .where(col(Employee.role) != "")
            .distinct()
            .order_by(Employee.role)
        )
        result = await self._session.exec(query)
        rows = result.all()
        return [str(r) for r in rows if r]

    async def list_personnel_types(self) -> list[str]:
        """获取人员类型列表(在编/外部人力资源 两个固定选项)。"""
        return ["在编", "外部人力资源"]

    async def list_employee_statuses(self) -> list[str]:
        """获取员工状态列表(distinct)。"""
        query = (
            select(Employee.employee_status)
            .where(col(Employee.employee_status).isnot(None))
            .where(col(Employee.employee_status) != "")
            .distinct()
            .order_by(Employee.employee_status)
        )
        result = await self._session.exec(query)
        rows = result.all()
        return [str(r) for r in rows if r]

    async def list_by_department(self, department: str, level: int = 2) -> Sequence[Employee]:
        """按部门获取人员列表。"""
        dept_col = getattr(Employee, f"level{level}_dept")
        query = select(Employee).where(dept_col == department).order_by(Employee.name)
        result = await self._session.exec(query)
        return result.all()

    async def get(self, employee_id: int) -> Employee | None:
        """按 ID 获取员工。"""
        return await self._session.get(Employee, employee_id)

    async def list_all(self) -> Sequence[Employee]:
        """获取全部员工。"""
        result = await self._session.exec(select(Employee).order_by(col(Employee.id)))
        return result.all()
