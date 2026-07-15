"""统一业务异常 + 全局异常处理器。

Service 层只抛与传输无关的业务异常(AppError 及其子类),
由这里集中映射成 HTTP 状态码, 保持路由层干净、可复用。
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """业务异常基类。默认映射为 400。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """资源不存在。映射为 404。"""

    def __init__(self, resource: str, identifier: object) -> None:
        super().__init__(f"{resource} not found: {identifier!r}")
        self.resource = resource
        self.identifier = identifier


def register_exception_handlers(app: FastAPI) -> None:
    """把业务异常注册为统一的 HTTP 响应。团队新增异常类型时在此追加映射。"""

    @app.exception_handler(NotFoundError)
    async def _handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})
