"""Service 层单元测试: 用假 Repository 隔离数据库, 只验证业务逻辑。

这正是三层的价值——Repository 是 seam, service 不依赖真实库即可单测
(对应 TDD 规范里的"Mock 外部依赖 DB")。真实 Repository 由接口集成测试覆盖。
生产可把 Repository 抽成 Protocol 做依赖倒置, 母版从简用假实现。
"""

import pytest

from app.core.exceptions import NotFoundError
from app.models.item import Item, ItemCreate
from app.services.item_service import ItemService


class FakeItemRepository:
    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._seq = 0

    async def add(self, item: Item) -> Item:
        if item.id is None:
            self._seq += 1
            item.id = self._seq
        self._items[item.id] = item
        return item

    async def get(self, item_id: int) -> Item | None:
        return self._items.get(item_id)

    async def list(self) -> list[Item]:
        return list(self._items.values())

    async def delete(self, item: Item) -> None:
        if item.id is not None:
            self._items.pop(item.id, None)


def _service() -> ItemService:
    # 假 Repository 与真类接口一致, 类型上用 ignore 声明替身。
    return ItemService(FakeItemRepository())  # type: ignore[arg-type]


async def test_should_raise_not_found_when_getting_missing_item() -> None:
    with pytest.raises(NotFoundError):
        await _service().get(999)


async def test_should_create_then_read_back_item() -> None:
    service = _service()

    created = await service.create(ItemCreate(name="widget", quantity=3))

    assert created.id is not None
    fetched = await service.get(created.id)
    assert fetched.name == "widget"
    assert fetched.quantity == 3
