---
name: capacity-analysis-v2-adr
description: 产能分析系统 v2 关键架构决策: 数据源抽象 Provider 模式、自引用项目分类表、导入时预计算应有产能与项目匹配、下钻用 Modal+面包屑
metadata:
  type: project
---

# 产能分析系统 v2 ADR 新增决策

## ADR-5: 项目分类用自引用树形表

**决策**: 采用 `project_categories` 自引用表(id, name, level, parent_id, sort_order)存储三级分类体系。

**Why:** 需求明确要求"项目分类体系动态可配置, 不硬编码"。树形结构用自引用表最灵活, 13 条记录无性能问题。如果未来需要四级/五级分类, 改配置即可, 不用改表结构。

**How to apply:** 类似"层级分类"需求均用自引用表, 不为层级数写死字段。

## ADR-6: 数据源抽象 Provider 模式

**Decision:** 用 `DataSourceProvider` 抽象类(5 个方法: provide_employees/work_hours/project_categories/holidays/three_fast_plans)隔离数据源, 当前 Excel 实现在 `ExcelDataSourceProvider`, 未来 API 实现只需实现同一接口。

**Why:** 需求明确未来可能从 API 接口读取。Iterator 模式处理大数据量, list 模式处理小数据量(分类/节假日)。上层 DataImportService 不直接依赖 pandas/openpyxl。

**How to apply:** 所有需要"先读 Excel 后切 API"的场景均采用 Provider 抽象模式。

## ADR-7: 工时项目在导入时匹配分类 + 后续可重匹配

**Decision:** 项目名清洗 + 分类匹配在导入时执行, 结果存入 `work_hours.category_id`。提供 `POST /data-import/rematch-categories` 端点支持配置更新后单独重新匹配。

**Why:** 写入一次查询多次, 避免每次聚合查询都做字符串处理。重匹配端点解决分类配置变更场景。

**How to apply:** 类似"数据预处理后存储"模式用于报表型系统。

## ADR-8: 应有产能预计算存储

**Decision:** 应有产能(按人+月)在导入时预计算并存储到 `should_be_capacity` 表。

**Why:** 计算逻辑含逐日遍历, 194 人 x 6 月 = ~36K 次日历遍历。预计算后查询只需简单 SUM+JOIN, 响应时间从秒级降到毫秒级。

**How to apply:** 面向报表的聚合预计算写入专用表, 常见于 BI/看板类系统。

## ADR-9: 下钻用 Modal + 面包屑 + 逐层请求

**Decision:** 数据穿透用 Modal 弹窗 + 面包屑导航, 每层独立 API 请求, 不预加载全量数据。

**Why:** Modal 不丢失主页面状态, 面包屑支持任意回退。逐层请求控制 payload 大小, 避免下发全量明细。

**How to apply:** 多维数据下钻通用模式, 每条穿透路径定义清晰的"路径键"(dept_path / category_id / project_name / employee_id)。

## 与 v1 ADR 的关系

v1 的 ADR-1(不建独立项目/部门表)、ADR-2(偏离度 service 层)、ADR-3(query params 筛选)、ADR-4(Modal 下钻)在 v2 中全部沿用, v2 在上述基础上新增 5 个架构决策。

[[capacity-analysis-adr]]
