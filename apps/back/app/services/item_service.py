"""Item 服务层: 只做业务逻辑编排, 数据访问下沉到 Repository。

- 依赖 ItemRepository, 不直接碰 session / SQL。
- 抛与传输无关的业务异常(NotFoundError), 由全局处理器映射为 HTTP。
- 团队的业务规则(校验、状态流转、跨实体编排)都写在这一层。
"""

from app.core.exceptions import NotFoundError
from app.core.time import utcnow
from app.models.item import Item, ItemCreate, ItemUpdate
from app.models.pagination import Page
from app.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    async def create(self, payload: ItemCreate) -> Item:
        item = Item.model_validate(payload.model_dump())
        return await self._repository.add(item)

    async def get(self, item_id: int) -> Item:
        item = await self._repository.get(item_id)
        if item is None:
            raise NotFoundError(resource="Item", identifier=item_id)
        return item

    async def list_page(self, limit: int, offset: int) -> Page[Item]:
        items = list(await self._repository.list(limit, offset))
        total = await self._repository.count()
        return Page(items=items, total=total, limit=limit, offset=offset)

    async def count(self) -> int:
        return await self._repository.count()

    async def update(self, item_id: int, payload: ItemUpdate) -> Item:
        item = await self.get(item_id)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        item.updated_at = utcnow()
        return await self._repository.add(item)

    async def delete(self, item_id: int) -> None:
        item = await self.get(item_id)
        await self._repository.delete(item)
