"""Item 路由层(Controller, 薄): 只收参/返 DTO, 业务逻辑全在 service。

只用 GET / POST: 更新与删除走 POST 子路径, 不使用 PATCH/PUT/DELETE。
列表用 GET query 参数分页(limit/offset)。
"""

from fastapi import APIRouter, Query, status

from app.api.deps import ItemServiceDep
from app.models.item import Item, ItemCreate, ItemPublic, ItemUpdate
from app.models.pagination import Page

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate, service: ItemServiceDep) -> Item:
    return await service.create(payload)


@router.get("", response_model=Page[ItemPublic])
async def list_items(
    service: ItemServiceDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[Item]:
    return await service.list_page(limit, offset)


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
