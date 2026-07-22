# Dockerfile —— 多阶段构建, 同源单进程(一个容器跑完前端 + API)
#
# 构建: docker build -t agent-driven-gen .
# 运行: docker run -p 8901:8901 -v app-data:/app/apps/back/data agent-driven-gen
# 或用 docker compose up(见 docker-compose.yml)

# ---- Stage 1: 构建前端 ----
FROM node:20-alpine AS frontend
RUN corepack enable pnpm
WORKDIR /build

# 先拷依赖描述(利用 Docker 层缓存)
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/
RUN pnpm install --frozen-lockfile

# 拷源码 + 端口配置(vite.config.ts 读 ports.json), 构建
COPY apps/web/ ./apps/web/
COPY ports.json ./
RUN pnpm --filter web build

# ---- Stage 2: 运行时(同源单进程) ----
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS runtime
ENV UV_LINK_MODE=copy
WORKDIR /app/apps/back

# 先拷依赖描述(利用缓存), 跳过 dev 依赖(ruff/mypy/pytest)
COPY apps/back/pyproject.toml apps/back/uv.lock ./
RUN uv sync --no-dev

# 拷后端源码
COPY apps/back/ ./

# 拷前端构建产物
COPY --from=frontend /build/apps/back/static ./static

# SQLite 数据持久化目录(docker volume 挂载)
RUN mkdir -p data logs

ENV APP_DATABASE_URL=sqlite+aiosqlite:///./data/dev.db
ENV APP_LOGGING__SQL_ECHO=false
ENV APP_LOGGING__DIR=logs

EXPOSE 8901

# Alembic 迁移在 lifespan 自动跑, 无需额外命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8901"]
