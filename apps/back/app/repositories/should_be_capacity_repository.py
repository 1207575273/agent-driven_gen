"""ShouldBeCapacity 仓储层(DAO): 应有产能数据访问。"""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import func
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.should_be_capacity import ShouldBeCapacity


def _dept_col(level: int) -> ColumnElement[str]:  # type: ignore[misc]
    mapping: dict[int, Any] = {  # type: ignore[dict-item]
        1: Employee.level1_dept,  # type: ignore[dict-item]
        2: Employee.level2_dept,  # type: ignore[dict-item]
        3: Employee.level3_dept,  # type: ignore[dict-item]
        4: Employee.level4_dept,  # type: ignore[dict-item]
    }
    col_val = mapping.get(level, Employee.level2_dept)  # type: ignore[assignment]
    return col_val  # type: ignore[return-value]


class ShouldBeCapacityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_employee_month(self, employee_id: int, year_month: str) -> ShouldBeCapacity | None:
        stmt = select(ShouldBeCapacity).where(
            ShouldBeCapacity.employee_id == employee_id, ShouldBeCapacity.year_month == year_month
        )
        result = await self._session.exec(stmt)
        return result.first()

    async def list_by_employee(self, employee_id: int) -> Sequence[ShouldBeCapacity]:
        stmt = (
            select(ShouldBeCapacity)
            .where(ShouldBeCapacity.employee_id == employee_id)
            .order_by(col(ShouldBeCapacity.year_month))
        )
        result = await self._session.exec(stmt)
        return result.all()

    async def list_by_month(self, year_month: str) -> Sequence[ShouldBeCapacity]:
        stmt = (
            select(ShouldBeCapacity)
            .where(ShouldBeCapacity.year_month == year_month)
            .where(ShouldBeCapacity.capacity_days > 0)
            .order_by(col(ShouldBeCapacity.employee_id))
        )
        result = await self._session.exec(stmt)
        return result.all()

    async def aggregate_by_dept_month(
        self, year_months: list[str], dept_level: int = 2, employee_ids: list[int] | None = None
    ) -> Sequence[dict[str, object]]:
        dept_raw = _dept_col(dept_level)
        dept_col_labeled: Any = dept_raw.label("dept_name")  # type: ignore[explicit-any]
        sum_cap = func.sum(ShouldBeCapacity.capacity_days)
        sum_work = func.sum(ShouldBeCapacity.total_working_days)
        cnt_emp = func.count(func.distinct(ShouldBeCapacity.employee_id))
        stmt = (
            select(dept_col_labeled, ShouldBeCapacity.year_month, sum_cap, sum_work, cnt_emp)  # type: ignore[call-overload]
            .select_from(ShouldBeCapacity)
            .join(Employee, ShouldBeCapacity.employee_id == Employee.id)  # type: ignore[arg-type]
            .where(col(ShouldBeCapacity.year_month).in_(year_months))
        )
        stmt = stmt.group_by(dept_raw, ShouldBeCapacity.year_month).order_by(dept_raw, ShouldBeCapacity.year_month)
        if employee_ids:
            stmt = stmt.where(col(ShouldBeCapacity.employee_id).in_(employee_ids))
        result = await self._session.exec(stmt)
        rows = result.all()
        return [
            _row_to_dict(row, ["dept_name", "month", "should_be_days", "total_working_days", "person_count"])
            for row in rows
        ]

    async def aggregate_by_month(
        self, year_months: list[str], employee_ids: list[int] | None = None
    ) -> Sequence[dict[str, object]]:
        stmt = (
            select(
                ShouldBeCapacity.year_month,
                func.sum(ShouldBeCapacity.capacity_days),
                func.sum(ShouldBeCapacity.total_working_days),
                func.count(func.distinct(ShouldBeCapacity.employee_id)),
            )
            .where(col(ShouldBeCapacity.year_month).in_(year_months))
            .group_by(ShouldBeCapacity.year_month)
            .order_by(ShouldBeCapacity.year_month)
        )
        if employee_ids:
            stmt = stmt.where(col(ShouldBeCapacity.employee_id).in_(employee_ids))
        result = await self._session.exec(stmt)
        rows = result.all()
        return [
            _row_to_dict(row, ["year_month", "should_be_days", "total_working_days", "person_count"]) for row in rows
        ]

    async def get_total_by_period(
        self, year_months: list[str], employee_ids: list[int] | None = None
    ) -> dict[str, object]:
        stmt = select(
            func.sum(ShouldBeCapacity.capacity_days), func.count(func.distinct(ShouldBeCapacity.employee_id))
        ).where(col(ShouldBeCapacity.year_month).in_(year_months))
        if employee_ids:
            stmt = stmt.where(col(ShouldBeCapacity.employee_id).in_(employee_ids))
        result = await self._session.exec(stmt)
        row = result.first()
        if row is None:
            return {"should_be_days": 0.0, "person_count": 0}
        return {"should_be_days": float(row[0] or 0), "person_count": int(row[1] or 0)}


def _row_to_dict(row: object, keys: list[str]) -> dict[str, object]:
    result: dict[str, object] = {}
    for i, key in enumerate(keys):
        try:
            result[key] = row[i]  # type: ignore[index]
        except (IndexError, TypeError):
            try:
                result[key] = getattr(row, key)
            except AttributeError:
                result[key] = None
    return result
