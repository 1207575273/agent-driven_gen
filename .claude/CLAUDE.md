# CLAUDE.md(项目级工程约束)

本文件是本项目的工程宪法。与全局 `~/.claude/CLAUDE.md` 冲突时,**以本文件为准**(项目优先)。
所有代码、文档、提交、回复一律中文,**禁用 emoji 与装饰字符**(状态用 `[PASS]/[FAIL]/[WARN]/[INFO]`,箭头用 `->`)。

---

## 一、最高原则

- 两道筛子:**超级架构师**(可落地、可扩展、可迭代)+ **超级产品**(解决什么问题、对谁有价值)。
- **KISS & YAGNI**:如无必要勿增实体。本项目是给 PMO/测试 fork 的极简种子,不预置鉴权/部署/业务横切。
- 高内聚低耦合,每个模块/函数只做一件事;卫语句优先,嵌套不超过 3 层。

## 二、后端硬约束(不可违反)

- **完整三层**:`route`(薄控制器,`app/api/v1/`)-> `service`(业务,`app/services/`)-> `repository`(数据访问,`app/repositories/`)。依赖链 `session -> repository -> service -> route`,在 `app/api/deps.py` 装配。禁止跨层。
- **只用 GET / POST**:查询 GET;写操作 POST;更新 `POST /{id}/update`,删除 `POST /{id}/delete`。禁止 PATCH/PUT/DELETE。
- **API 版本化**:路由挂 `app/api/v1/`。
- **模型 = SQLModel 全家桶**:`XxxBase / Xxx(table=True) / XxxCreate / XxxUpdate / XxxPublic`,新增实体在 `app/db/base.py` import 一次。
- **事务边界**统一在 `app/db/session.py` 的 `get_session`(请求级 UoW,成功 commit / 异常 rollback);仓储只 flush 不 commit。
- **异常**:service 抛业务异常(`app/core/exceptions.py`),由全局处理器映射为 HTTP;禁吞异常、禁空 catch。

## 三、前端约束(轻)

- Vite + React 18 + TypeScript **strict**;**禁用 `any`**;UI 与业务逻辑分离。
- 服务端数据用 React Query,纯 UI 状态用 Zustand;只用 GET/POST 调后端;openapi 客户端不强制。

## 四、质量基座(编译期替身)

- Python 无编译期,靠 **`Ruff + mypy(strict) + pytest`** 三道防线兜底;前端 **`Biome + tsc + Vitest`**。
- `mypy strict` 从严:只允许最小化 `# type: ignore[code]` 精确豁免,禁止整文件关检查。
- 后端测试覆盖率 **>= 80%**;service 用假 repository 单测,接口用 httpx client 集成测。
- **自查一键**:`pnpm check`(或双击 `check.bat`),不拦提交;工程成熟后再按方案文档附录 A 启用 pre-commit + CI。

## 五、运行与部署

- 开发:`pnpm dev`(读 `ports.json` 探测空闲端口起前后端,冲突自动跳,全占用报错;前端 `/api` 代理到后端实际端口)。
- 生产:`pnpm build` -> `pnpm start`(后端单进程同源托管前端 + API)。
- SQL 日志默认打印(`APP_SQL_ECHO=true`),生产设 `false`。

## 六、通用编码规范

- 命名用业务语义,禁无意义缩写(循环 `i/j/k` 除外);魔法值提常量/枚举;注释解释 Why 而非 What;日志打关键参数并脱敏。

## 七、多 Agent 分工(`.claude/agents/`)

流水线:`需求 -> 架构 -> [后端 / 前端] 并行 -> 测试`。

| Agent | 职责 | 边界 |
|-------|------|------|
| `requirements-analyst` | 澄清需求、定义 Done、划边界、剔 YAGNI | 只读 + 写 docs,不出方案、不写码 |
| `architect` | 接口契约、模块拆分、任务拆解(守本文约束) | 只读 + 写 docs,不写实现码 |
| `backend-engineer` | FastAPI 三层实现,收尾跑 `pnpm check:back` | 读写 + Bash |
| `frontend-engineer` | React 实现,收尾跑 `pnpm check:web` | 读写 + Bash |
| `test-engineer` | pytest / Vitest / Playwright E2E / curl,守 TDD 与覆盖率 | 读写 + Bash |

## 八、Git

- 提交遵循 Conventional Commits(`feat:` / `fix:` / `refactor:` / `docs:` / `chore:`)。

