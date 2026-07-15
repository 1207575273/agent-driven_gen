"""Item 路由层(Controller, 薄): 只收参/返 DTO, 业务逻辑全在 service。

只用 GET / POST: 更新与删除走 POST 子路径, 不使用 PATCH/PUT/DELETE。
"""

from collections.abc import Sequence

from fastapi import APIRouter, status

from app.api.deps import ItemServiceDep
from app.models.item import Item, ItemCreate, ItemPublic, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, service: ItemServiceDep) -> Item:
    return await service.create(payload)


@router.get("", response_model=list[ItemPublic])
async def list_items(service: ItemServiceDep) -> Sequence[Item]:
    return await service.list()


@router.get("/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int, service: ItemServiceDep) -> Item:
    return await service.get(item_id)


@router.post("/{item_id}/update", response_model=ItemPublic)
async def update_item(item_id: int, payload: ItemUpdate, service: ItemServiceDep) -> Item:
    return await service.update(item_id, payload)


@router.post("/{item_id}/delete")
async def delete_item(item_id: int, service: ItemServiceDep) -> dict[str, bool]:
    await service.delete(item_id)
    return {"success": True}
