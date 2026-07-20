# CLAUDE.md(项目工程宪法)

项目优先于全局。全程中文,禁 emoji(状态 [PASS]/[FAIL],箭头 ->)。给 PMO/测试 fork 的极简种子,KISS & YAGNI,不预置鉴权/部署/业务横切。

## 一、后端硬约束

完整三层:route(薄控制器,`api/v1/`)-> service(业务)-> repository(数据访问),依赖链 `session -> repository -> service -> route` 在 `api/deps.py` 装配,禁跨层。**只用 GET/POST**:更新走 `POST /{id}/update`,删除走 `POST /{id}/delete`。模型用 SQLModel 全家桶并在 `db/base.py` 注册;事务边界统一在 `get_session`;service 抛业务异常、由全局处理器映射,禁吞异常。

## 二、质量与规范

后端 `Ruff + mypy(strict) + pytest`(覆盖率 >=80%)、前端 `Biome + tsc + Vitest` 三道防线,一键 `pnpm check` 自查(不拦提交)。前端 TS strict、禁 `any`,UI 与逻辑分离。命名用业务语义,卫语句(嵌套 <=3),魔法值提常量,日志脱敏。

## 三、Agent 与运行

**简单需求直接在主会话 / 主 Agent 干完,不启动这套流水线**;仅当多模块、需求模糊或工作量大时才拆到 agent:`需求 -> 架构 -> [后端 / 前端] -> 测试`(见 `.claude/agents/`)。走流水线时各 Agent 完成后尽量产出任务文档到 `docs/<YYYYMMDDHHMMSS-任务>/{需求,架构,前端,后端,测试}/`,成规模工作必留档并尽量配架构图/流程图/用例图(Mermaid);归集规范以 `docs/README.md` 为单一事实源,强制遵循。开发 `pnpm dev`(读 `ports.json` 探测端口),生产 `pnpm build` + `pnpm start`(后端同源托管前端 + API)。提交遵循 Conventional Commits,作者 
xxxx
