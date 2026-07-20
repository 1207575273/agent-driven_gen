"""FastAPI 应用入口: 组装路由、异常处理、定时任务、前端静态托管(含 SPA 兜底)。"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response
from starlette.types import Scope

from app.api.v1 import api_router as v1_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware
from app.core.scheduler import register_jobs, scheduler
from app.db.migrate import run_migrations_to_head


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # pragma: no cover
    # 建表统一走 Alembic 迁移(migrations/), 不用 create_all —— 见 db/migrate.py 的动机说明。
    # env.py 在 online 模式自行 asyncio.run, 故放到独立线程避免与本事件循环嵌套。
    await asyncio.to_thread(run_migrations_to_head)
    # 进程内定时任务: 随应用起停(单进程同源, 不另起 worker)。
    register_jobs()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


class SpaStaticFiles(StaticFiles):
    """SPA 兜底: 找不到文件(404)时回 index.html。

    前端用 react-router 客户端路由后, 深链(如 /items)刷新会直接打后端;
    没有兜底就 404。这里把"既非 API 又非真实文件"的路径统一回 index.html,
    交给前端路由接管。
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


def create_app() -> FastAPI:
    configure_logging(settings.logging)
    app = FastAPI(title="通用母版 API", lifespan=lifespan)
    register_exception_handlers(app)
    # 请求追踪: 每个请求绑定 request_id 贯穿日志 + 回写响应头(后添加者最外层, 包住整条链)。
    app.middleware("http")(request_id_middleware)
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
    # 前端 pnpm build 输出到 apps/back/static, 存在则由后端一并托管(含 SPA 兜底)。
    # 挂在 API 路由之后: /api/* 先被路由匹配, 其余路径才落到这里。
    static_dir = Path(__file__).resolve().parent.parent / "static"
    if static_dir.exists():  # pragma: no cover
        app.mount("/", SpaStaticFiles(directory=static_dir, html=True), name="static")


app = create_app()
