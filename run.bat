@echo off
REM 傻瓜一键起(Windows): 装依赖 -> pnpm dev(自动探测端口, 起后端 + 前端)
setlocal
set "ROOT=%~dp0"

echo [INFO] 安装后端依赖 (uv sync)...
call uv sync --directory "%ROOT%apps\back" || goto :error

echo [INFO] 安装前端依赖 (pnpm install)...
pushd "%ROOT%" && call pnpm install || goto :error
popd

echo [INFO] 启动 (端口见 ports.json, 自动探测空闲端口)...
pushd "%ROOT%" && call pnpm dev
popd
goto :eof

:error
echo [FAIL] 启动失败, 请检查上面的错误输出。
exit /b 1
