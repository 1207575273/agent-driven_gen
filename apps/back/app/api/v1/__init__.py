"""API v1 聚合路由。新增业务模块时在此 include_router。"""

from fastapi import APIRouter

from app.api.v1 import dashboard, departments, filters, health, items, projects, roles, system

api_router = APIRouter()
api_router.include_router(dashboard.router)
api_router.include_router(departments.router)
api_router.include_router(filters.router)
api_router.include_router(health.router)
api_router.include_router(items.router)
api_router.include_router(projects.router)
api_router.include_router(roles.router)
api_router.include_router(system.router)
