"""FastAPI 应用入口: 组装路由、异常处理、前端静态托管。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_router as v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.db.base import metadata
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    # 母版起步用 create_all 建表, 便于开箱即跑;
    # 生产环境请改用 Alembic 迁移(migrations/), 并移除这里的 create_all。
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield


def create_app() -> FastAPI:
    configure_logging(settings.log_level, sql_echo=settings.sql_echo)
    app = FastAPI(title="通用母版 API", lifespan=lifespan, default_response_class=ORJSONResponse)
    register_exception_handlers(app)
    app.include_router(v1_router, prefix=f"{settings.api_prefix}/v1")
    _mount_static(app)
    return app


def _mount_static(app: FastAPI) -> None:
    # 前端 `pnpm build` 输出到 apps/back/static, 存在则由后端一并托管。
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():  # pragma: no cover
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


app = create_app()
