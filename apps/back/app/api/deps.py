"""依赖注入装配: session -> repository -> service。

路由只需声明 `service: ItemServiceDep`, FastAPI 自动构造整条链。
团队新增实体时照此再写一组 get_xxx_repository / get_xxx_service 即可。
"""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService
from app.services.system_service import SystemService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_item_repository(session: SessionDep) -> ItemRepository:
    return ItemRepository(session)


ItemRepositoryDep = Annotated[ItemRepository, Depends(get_item_repository)]


def get_item_service(repository: ItemRepositoryDep) -> ItemService:
    return ItemService(repository)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# 系统指标: 无 session/repository, 直接构造 service。
def get_system_service() -> SystemService:
    return SystemService()


SystemServiceDep = Annotated[SystemService, Depends(get_system_service)]

# 鉴权占位(母版不含鉴权)。团队接入后在此提供:
# async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)) -> User: ...
# CurrentUserDep = Annotated[User, Depends(get_current_user)]
