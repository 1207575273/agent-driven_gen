"""请求追踪中间件: 为每个请求绑定 request_id, 贯穿日志并回写响应头。

可观测性的通用地基 —— 任何内部系统排障都需要"把一次请求的所有日志串起来":

- 入站带 `X-Request-ID` 则透传(便于跨服务串联), 否则生成一个。
- 用 `structlog.contextvars.bind_contextvars` 绑定到上下文; logging.py 的
  `merge_contextvars` 会把它自动注入这次请求产生的每一条日志(无需各处手传)。
- 响应回写 `X-Request-ID`, 前端 / 调用方可拿到用于对账、报障。

母版只做这一层最小追踪; 接入 OpenTelemetry / 分布式 trace 时在此扩展(seam)。
"""

import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
    structlog.contextvars.bind_contextvars(request_id=request_id)
    try:
        response = await call_next(request)
    finally:
        # 无论成功或异常都清理, 避免 contextvar 泄漏到复用的事件循环任务。
        structlog.contextvars.clear_contextvars()
    response.headers[REQUEST_ID_HEADER] = request_id
    return response
