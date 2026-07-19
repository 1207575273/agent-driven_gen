"""Employee 仓储层(DAO): 花名册数据访问。"""

from collections.abc import Sequence

from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee


class EmployeeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Employee]:
        result = await self._session.exec(select(Employee).order_by(col(Employee.id)))
        return result.all()

    async def list_active_normal(self) -> Sequence[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.is_excluded == False)  # noqa: E712
            .where(Employee.employee_status != "离职")
            .order_by(col(Employee.id))
        )
        result = await self._session.exec(stmt)
        return result.all()

    async def list_departments(self, level: int = 2) -> Sequence[str]:
        dept_col: ColumnElement[str] | None = _dept_col(Employee, level)
        safe_col: ColumnElement[str] = dept_col if dept_col is not None else Employee.level2_dept  # type: ignore[assignment,return-value]
        stmt = select(safe_col).where(safe_col.isnot(None)).distinct().order_by(safe_col)  # type: ignore[arg-type]
        result = await self._session.exec(stmt)
        return [r for r in result.all() if r is not None]

    async def list_roles(self) -> Sequence[str]:
        stmt = select(Employee.role).where(Employee.role.isnot(None)).distinct().order_by(Employee.role)  # type: ignore[union-attr,arg-type]
        result = await self._session.exec(stmt)
        return [r for r in result.all() if r is not None]

    async def list_by_department(self, dept_level: int, dept_name: str) -> Sequence[Employee]:
        dept_col: ColumnElement[str] | None = _dept_col(Employee, dept_level)
        if dept_col is None:
            dept_col = Employee.level2_dept  # type: ignore[assignment]
        stmt = select(Employee).where(dept_col == dept_name).order_by(col(Employee.id))  # type: ignore[arg-type]
        result = await self._session.exec(stmt)
        return result.all()

    async def get(self, employee_id: int) -> Employee | None:
        return await self._session.get(Employee, employee_id)

    async def get_by_employee_id_str(self, employee_id_str: str) -> Employee | None:
        stmt = select(Employee).where(Employee.employee_id == employee_id_str)
        result = await self._session.exec(stmt)
        return result.first()

    async def get_by_name(self, name: str) -> Employee | None:
        stmt = select(Employee).where(Employee.name == name)
        result = await self._session.exec(stmt)
        return result.first()


def _dept_col(model: type[Employee], level: int) -> ColumnElement[str] | None:
    mapping: dict[int, ColumnElement[str]] = {
        1: model.level1_dept,  # type: ignore[dict-item]
        2: model.level2_dept,  # type: ignore[dict-item]
        3: model.level3_dept,  # type: ignore[dict-item]
        4: model.level4_dept,  # type: ignore[dict-item]
    }
    return mapping.get(level)
