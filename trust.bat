@echo off
REM 一键信任本项目 (Windows 双击运行即可)。
REM 真正的逻辑在 scripts\trust.mjs, 本脚本只负责: 切 UTF-8、检测 node、转交执行。
chcp 65001 >nul
setlocal

where node >nul 2>nul
if errorlevel 1 (
  echo [FAIL] 未找到 node, 请先安装 Node.js 并加入 PATH 后重试。
  pause
  exit /b 1
)

node "%~dp0scripts\trust.mjs"
if errorlevel 1 (
  echo [FAIL] 执行失败, 详见上方输出。
  pause
  exit /b 1
)

echo.
echo 完成, 按任意键关闭。
pause >nul
