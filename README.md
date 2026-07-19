# 通用 monorepo 母版

一套极简、可 fork 的**全栈**脚手架:前端 + 后端 + 质量闸门一次备齐。任何 web 业务、任何形态(内部工具、后台系统、数据看板、审批 / CRUD)都照着 Item 示例往外长即可。团队(PMO、测试等)clone 出去就能迭代自己的系统。

母版只保证两件事:**开箱能跑通** + **写不进烂代码**(硬性质量闸门)。

## 为什么是它(价值)

- **一套整完前后端**:一个仓库、一条 `pnpm dev` 起飞,前端(React)+ 后端(FastAPI)+ 三道质量闸门全接好,不用自己从零拼脚手架。
- **部署极简,无需 nginx**:生产是**同源单进程** —— `pnpm build` 把前端打进后端 `static`,`pnpm start` 起**一个** uvicorn 同时托管前端页面与 `/api`。没有反向代理、没有 nginx、没有跨域、没有多进程编排:**一个端口、一个进程、一台机器**就上线。
- **任何 web 业务、任何形态**:完整三层 + 配置化前端,CRUD / 看板 / 审批 / 报表都能往外长;全程只用 GET / POST,心智极简。
- **写不进烂代码**:Python 无编译期,靠 Ruff + mypy(strict) + pytest(覆盖率 ≥ 80%)+ 前端 Biome / tsc / Vitest 兜底,一键 `pnpm check` 自查。

## 一支单进程的 Agent 团队(需求 → 测试)

`.claude/agents/` 里放了 5 个角色 Agent,由主会话在**同一进程 / 会话**内按流水线协作 —— 这是"Agent 团队"的最简形态:只靠几个 markdown 文件,无需 tmux / 多进程 / 后台编排。

```
需求分析 -> 架构设计 -> [后端 / 前端 并行实现] -> 测试
```

- **完整交付链**:从需求澄清、接口契约、分层实现到测试守闸一条链走完;每步产出任务文档到 `docs/<时间戳-任务>/`(见 `docs/README.md`),尽量配架构图 / 流程图 / 用例图。(严格意义的"全闭环"还含评审 / 部署 / 线上反馈,可按需再接。)
- **越用越懂这个项目**:5 个 Agent 都开了项目级持久记忆(`memory: project` -> `.claude/agent-memory/<agent>/`,随仓库共享)。用得越多、沉淀越多(套路 / 踩坑 / 决策),Agent 对**本项目**就越熟。前提是认真维护 `MEMORY.md`(启动只载入前 200 行)并提交共享 `.claude/agent-memory/` —— 它长的是"对项目的了解",不是模型本身变聪明。
- **按需启动**:简单需求直接在主会话干完,不必拉这套流水线;多模块、需求模糊或工作量大时才拆到 Agent。

## 技术栈

| 层 | 选型 |
|----|------|
| Monorepo | pnpm workspace + uv |
| 后端 | FastAPI + SQLModel + SQLite(WAL) + Alembic |
| 后端质量 | Ruff(lint/format) + mypy(strict, 编译期替身) + pytest(覆盖率闸门) |
| 前端 | Vite + React + TypeScript(strict) + Zustand + React Query + ECharts |
| 前端质量 | Biome(lint/format) + tsc + Vitest |
| 后端基座 | 定时任务 APScheduler(进程内) · 日志 structlog(控制台人读 + 文件 JSONL) · 配置 pydantic-settings(env + .env, 12-factor) |
| 前端路由 | react-router(声明式);生产同源由后端 SPA 兜底 |
| 质量自查 | `pnpm check`(手动一键);pre-commit + CI 为未来可选(见方案文档附录) |

后端预置常用包:`httpx / orjson / structlog / tenacity / python-multipart / email-validator / pandas / openpyxl`(按需删减)。

## 前置条件(项目基座)

只需两样基座工具:**Node.js + pnpm**(前端与编排脚本)和 **uv**(Python 运行时与后端)。装好这两样,其余依赖由 `pnpm install` / `uv sync` 自动拉齐 —— 本机**不需要**预装 Python。

### 1. Node.js + pnpm

先装 Node.js LTS(>= 18),再装 pnpm:

```bash
# Node.js: 到 https://nodejs.org 下载 LTS, 或用 nvm / fnm 等版本管理器

# pnpm 方式一(Node 自带 Corepack, 推荐):
corepack enable pnpm

# pnpm 方式二(独立安装):
#   Windows(PowerShell):
Invoke-WebRequest https://get.pnpm.io/install.ps1 -UseBasicParsing | Invoke-Expression
#   macOS / Linux:
curl -fsSL https://get.pnpm.io/install.sh | sh -
#   或: npm install -g pnpm@latest-11   /   brew install pnpm
```

> 官方来源:安装文档 <https://pnpm.io/installation> · GitHub <https://github.com/pnpm/pnpm>

### 2. uv(自带并管理 Python 3.12,无需预装 Python)

```bash
#   Windows(PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
#   macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh
#   或: brew install uv   /   pipx install uv

# 备好 Python 3.12(可选; 后端命令 / pnpm build 首次运行会自动拉齐):
uv python install 3.12
```

> 官方来源:安装文档 <https://docs.astral.sh/uv/getting-started/installation/> · GitHub <https://github.com/astral-sh/uv>

> Windows 上这两条**安装命令用 PowerShell** 执行(一次性装工具);装好后日常开发再切回 Git Bash 跑 `./xxx.sh`。

### 3. 校验 + 首次装依赖

```bash
node -v && pnpm -v && uv --version    # 三个都打印版本号即就绪

pnpm install                          # 前端 + 编排脚本依赖
uv sync --directory apps/back         # 后端 Python 依赖(uv 顺带备好 Python 3.12)
```

装依赖也可直接跑 `./run.sh`(傻瓜一键:装好依赖并起开发)。

## 快速开始

> 母版统一只提供 `.sh` 脚本,不再维护 `.bat`。**Windows 用户请用 Git Bash**(Git for Windows 自带,右键"Git Bash Here"或在终端选 Git Bash)执行下面的 `./xxx.sh`,避免 CMD/PowerShell 的兼容与转义坑。

### 首次授信 Claude Code(一次即可)

克隆后先跑一次授信脚本,让本机的 Claude Code 免信任弹窗、直接应用本项目 `.claude/settings.json` 里声明的放行权限:

```bash
./trust.sh        # macOS / Linux / Windows(Git Bash)
```

- **它做什么**:只把"本项目路径"写进你自己 `~/.claude.json` 的信任标记,不改任何权限内容。改前自动备份、幂等,可反复跑。
- **为什么要脚本**:权限"声明"是项目级的(`.claude/settings.json` 随仓库共享:`acceptEdits` + `Bash`/读写编辑全放行,删除类命令仍二次确认);而"是否信任某目录"是用户级状态(每台机器各一份,无法随仓库共享),只能靠本机脚本补上。两者合一才达成"克隆后自动放行"。
- **注意**:运行前先关掉本项目正在跑的 Claude Code 会话,否则它退出时可能覆盖回写、抵消改动;脚本依赖 node 在 PATH(开发本就需要,一般已具备)。

### 开发

```bash
pnpm dev          # 自动探测端口起前后端(热更新)
# 或傻瓜一键(装依赖 + 起开发):
./run.sh          # macOS / Linux / Windows(Git Bash)
```

端口在顶层 `ports.json` 配置(默认后端 `8901-8903`、前端 `8911-8913` 候选)。`pnpm dev` 自动探测第一个空闲端口,全被占用则报错;前端 `/api` 自动代理到后端实际端口。

### 生产

```bash
pnpm build        # 前端产物 -> apps/back/static
pnpm start        # 起后端单进程, 同源托管前端 + API(默认端口 = ports.json backend[0])
# 换端口: PORT=80 pnpm start
```

生产是**同源单进程**:一个 uvicorn 同时提供 `/api/v1/*`(API)和 `/`(前端页面),不需要单独起前端。

## 目录结构

```
apps/
├── back/                    # 后端(FastAPI)
│   └── app/
│       ├── api/             # 路由层(薄控制器): 只收参/返 DTO
│       │   ├── deps.py      #   依赖注入装配: session -> repository -> service
│       │   └── v1/          #   版本化路由(items / health)
│       ├── services/        # 服务层: 业务逻辑编排(不碰 session/SQL)
│       ├── repositories/    # 仓储层(DAO): 数据访问, 持 session 写 SQLModel 查询
│       ├── models/          # SQLModel 实体 + 契约(全家桶)
│       ├── db/              # 引擎/会话(session) + 模型汇总(base)
│       ├── core/            # 配置 / 日志 / 时间 / 异常 / 安全占位
│       ├── main.py          # 应用入口
│       └── tests/           # pytest(内存 SQLite)
└── web/                     # 前端(React)
    └── src/
        ├── api/             # 轻量客户端(可选 openapi 生成)
        ├── components/      # 配置化动态表单等
        └── stores/          # Zustand 全局 UI 状态
```

## 分层约定:完整三层(薄控制器 / 服务 / 仓储)

| Java 分层 | 母版对应 | 职责 |
|-----------|----------|------|
| Controller | `app/api/v1/*.py` | 只管 HTTP: 收参、调 service、返 DTO。不写业务、不碰 SQL |
| Service | `app/services/*.py` | 业务逻辑编排 + 抛业务异常。调 repository, 不碰 session/SQL |
| Repository/DAO | `app/repositories/*.py` | 数据访问: 持 session, 用 SQLModel 写查询(add/get/list/delete) |
| Entity/DTO | `app/models/*.py` | SQLModel: Table + Create/Update/Public 契约 |
| 统一异常 | `app/core/exceptions.py` | 业务异常 -> HTTP 状态码的全局映射 |

依赖靠 FastAPI `Depends` 自动装配:`session -> repository -> service -> route`。
ORM 映射在 `models/`(`Item(table=True)` = `@Entity`),SQL 操作在 `repositories/`(`select()` = MyBatis Mapper)。

## HTTP 约定:只用 GET / POST

全项目只用两种方法。更新、删除走 POST 子路径,不用 PATCH/PUT/DELETE:

```
GET  /api/v1/items?limit&offset  分页列表(返回 {items,total,limit,offset})
GET  /api/v1/items/{id}       详情
POST /api/v1/items            新增
POST /api/v1/items/{id}/update  更新
POST /api/v1/items/{id}/delete  删除
```

## 后端基座能力

- **列表分页**:`GET /items?limit&offset` 返回 `{items,total,limit,offset}`;`limit` 1~100(默认 20)、`offset>=0`,越界 422。通用 `Page[T]`(`app/models/pagination.py`)团队新实体照抄。
- **定时任务**:进程内 APScheduler,随 `lifespan` 起停(单进程,不另起 worker)。`app/core/scheduler.py` 的 `register_jobs` 加 job;job 经 `session_scope()` + service 访问数据、守三层。多副本会重复触发(母版单 worker 无碍;多副本需外部调度 / 分布式锁,不预置)。
- **生产日志**:structlog 双出口 —— 控制台人读、文件 `logs/app.jsonl`(JSONL / UTC / 固定字段 `timestamp·level·logger·message` / 结构化异常);**8 小时滚动、留 10 天自动清理**。格式与滚动 / 留存由 `APP_LOGGING__*` 环境变量控制(见 `apps/back/.env`)。
- **配置服务**:pydantic-settings,优先级 `环境变量 > .env > 默认`(12-factor,无 YAML);K8s ConfigMap / Nacos 挂成 env 注入即可。`app/core/config.reload_settings()` 是热更 seam,供未来接配置中心 watcher。`apps/back/.env` 已随母版提交(仅无密钥默认值,fork 后开箱即用、想改直接改它);真实密钥 / 生产值一律用环境变量注入,勿写进已提交的 `.env`。
- **前端路由 + SPA 同源**:react-router 客户端路由;生产由后端 `SpaStaticFiles` 兜底(深链刷新回 `index.html`,不 404),仍单进程、无 nginx。

> 每项设计的"为什么 / 取舍"速查见 [架构决策记录](docs/架构决策记录.md)(ADR)。改母版前先看它,别无谓推翻已定权衡。

## 加一个新功能的标准动作(以实体 Foo 为例)

1. `app/models/foo.py` 定义 `FooBase / Foo(table) / FooCreate / FooUpdate / FooPublic`,并在 `app/db/base.py` import 一次。
2. `app/repositories/foo_repository.py` 写数据访问(持 `AsyncSession`,`add/get/list/delete`)。
3. `app/services/foo_service.py` 写业务逻辑(依赖 `FooRepository`,不碰 session/SQL)。
4. `app/api/deps.py` 加 `get_foo_repository` + `get_foo_service`。
5. `app/api/v1/foo.py` 写薄路由(只 GET/POST),在 `app/api/v1/__init__.py` include。
6. `app/tests/` 先写测试(TDD):service 用假 repository 单测,接口用 client 集成测。
7. 跑 `pnpm check`(或 `./check.sh`)自查 -> 全绿后提交 / 合并。

## 命令速查

```bash
pnpm dev       # 开发: 自动探测端口起前后端(热更新)
pnpm build     # 构建: 前端产物 -> apps/back/static
pnpm start     # 生产: 起后端单进程, 同源托管前端 + API
pnpm check     # 自查: 后端 Ruff+mypy+pytest / 前端 Biome+tsc+Vitest(或 ./check.sh)
```

单独跑某一项:`pnpm check:back` / `pnpm check:web` / `pnpm lint:back` / `pnpm type:back` / `pnpm test:back` 等。

## 质量基座说明

- Python 无编译期,靠 `Ruff + mypy(strict) + pytest` 三道防线模拟"编译期"。
- `mypy strict` 从严:母版从严,团队按需**局部**放宽,而不是反过来。
- 覆盖率闸门:后端 `>= 80%`。
- 现在:一键 `pnpm check`(不拦提交,想查就查);工程成熟后再启用 pre-commit + CI 硬闸门(配置见方案文档附录)。
- SQL 日志默认打印(`APP_SQL_ECHO=true`),生产设 `false`。
