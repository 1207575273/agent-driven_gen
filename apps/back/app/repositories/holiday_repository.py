"""Holiday 仓储层(DAO): 节假日数据访问。"""

from collections.abc import Sequence
from datetime import date

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.holiday import Holiday


class HolidayRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Holiday]:
        result = await self._session.exec(select(Holiday).order_by(col(Holiday.holiday_date)))
        return result.all()

    async def get_by_date(self, target_date: date) -> Holiday | None:
        stmt = select(Holiday).where(Holiday.holiday_date == target_date)
        result = await self._session.exec(stmt)
        return result.first()

    async def get_by_year_month(self, year_month: str) -> Sequence[Holiday]:
        """获取某月的所有节假日(含假期和补班)。"""
        year = int(year_month[:4])
        month = int(year_month[5:7])
        from calendar import monthrange

        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        stmt = (
            select(Holiday)
            .where(Holiday.holiday_date >= start)
            .where(Holiday.holiday_date <= end)
            .order_by(col(Holiday.holiday_date))
        )
        result = await self._session.exec(stmt)
        return result.all()

    async def get_holidays_by_month(self, year_month: str) -> Sequence[Holiday]:
        """获取某月的假期(is_workday=False)。"""
        all_in_month = await self.get_by_year_month(year_month)
        return [h for h in all_in_month if not h.is_workday]

    async def get_supplements_by_month(self, year_month: str) -> Sequence[Holiday]:
        """获取某月的补班日(is_workday=True)。"""
        all_in_month = await self.get_by_year_month(year_month)
        return [h for h in all_in_month if h.is_workday]
