"""API v1 聚合路由。新增业务模块时在此 include_router。"""

from fastapi import APIRouter

from app.api.v1 import capacity_audit, cross_analysis, data_import, drill_down, filters, health, items, system

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items.router)
api_router.include_router(system.router)
api_router.include_router(capacity_audit.router)
api_router.include_router(cross_analysis.router)
api_router.include_router(drill_down.router)
api_router.include_router(filters.router)
api_router.include_router(data_import.router)
