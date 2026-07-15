@echo off
REM 一键质量自查(不拦提交, 想查就跑, 双击即可):
REM   后端 Ruff + mypy(strict) + pytest, 前端 Biome + tsc + Vitest。
setlocal
cd /d "%~dp0"
call pnpm check
if errorlevel 1 (
  echo.
  echo [FAIL] 有检查未通过, 请看上面的输出。
  pause
  exit /b 1
)
echo.
echo [PASS] 全部检查通过。
pause
