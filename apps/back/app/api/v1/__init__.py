"""API v1 聚合路由。新增业务模块时在此 include_router。"""

from fastapi import APIRouter

from app.api.v1 import health, items, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items.router)
api_router.include_router(system.router)
