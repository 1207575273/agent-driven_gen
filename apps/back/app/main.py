"""FastAPI 应用入口: 组装路由、异常处理、前端静态托管。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    app = FastAPI(title="通用母版 API", lifespan=lifespan)
    register_exception_handlers(app)
    # CORS: 提前放行跨域。默认全放行(origins/methods/headers 皆 *);
    # 注意 allow_origins=["*"] 与 allow_credentials 不可同真(CORS 规范),
    # 若日后用 cookie 鉴权需带凭证, 改用 allow_origin_regex 指定来源。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router, prefix=f"{settings.api_prefix}/v1")
    _mount_static(app)
    return app


def _mount_static(app: FastAPI) -> None:
    # 前端 `pnpm build` 输出到 apps/back/static, 存在则由后端一并托管。
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():  # pragma: no cover
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


app = create_app()
