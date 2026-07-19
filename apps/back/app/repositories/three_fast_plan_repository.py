"""ThreeFastPlan 仓储层(DAO): 三快计划数据访问。"""

from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.three_fast_plan import ThreeFastPlan


class ThreeFastPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[ThreeFastPlan]:
        result = await self._session.exec(
            select(ThreeFastPlan).order_by(col(ThreeFastPlan.plan_quarter), col(ThreeFastPlan.category_id))
        )
        return result.all()

    async def get_by_quarter(self, plan_quarter: str) -> Sequence[ThreeFastPlan]:
        stmt = (
            select(ThreeFastPlan)
            .where(ThreeFastPlan.plan_quarter == plan_quarter)
            .order_by(col(ThreeFastPlan.category_id))
        )
        result = await self._session.exec(stmt)
        return result.all()

    async def get_by_category(self, category_id: int) -> Sequence[ThreeFastPlan]:
        stmt = (
            select(ThreeFastPlan)
            .where(ThreeFastPlan.category_id == category_id)
            .order_by(col(ThreeFastPlan.plan_quarter))
        )
        result = await self._session.exec(stmt)
        return result.all()
