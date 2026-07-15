"""Item 仓储层(Repository / DAO): 只封装数据访问, 不含任何业务规则。

- 持有 AsyncSession, 用 SQLModel 表达查询(这里就是"用 Python 写的 SQL")。
- 只做 add / get / list / delete 并 flush(拿自增主键), 不 commit ——
  事务边界由 db/session.get_session 统一控制。
- 团队新增实体照此在 app/repositories/ 下再写一个 XxxRepository。
"""

from collections.abc import Sequence

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.item import Item


class ItemRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, item: Item) -> Item:
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def get(self, item_id: int) -> Item | None:
        return await self._session.get(Item, item_id)

    async def list(self) -> Sequence[Item]:
        result = await self._session.exec(select(Item).order_by(col(Item.id)))
        return result.all()

    async def delete(self, item: Item) -> None:
        await self._session.delete(item)
        await self._session.flush()
