---
name: capacity-analysis-adr
description: 产能分析系统的关键架构决策(ADR): 不建独立项目/部门表、偏离度计算在 service 层、部门筛选走 query params、前端下钻优先用 Modal
metadata:
  type: project
---

# 产能分析系统 ADR 摘要

## ADR-1: 不建独立项目表/部门表

项目名和部门名直接从 work_hours 和 employees DISTINCT 查询, 不建独立表。
理由: 全量替换无需同步, 数据量小(59 项目/十来个部门), DISTINCT 开销可忽略。

## ADR-2: 偏离度计算放在 Service 层

个人偏离度 = (个人人天 - 同级均值) / 同级均值, 在 Python service 中计算而非 SQL。
理由: SQLite 窗口函数支持有限, Python 计算更直观、可测试, 169 人规模内存完全够用。

## ADR-3: 部门筛选用 query param 而非 path param

部门筛选用 `?department=技术部&level=2` 而非 `/departments/技术部/`。
理由: 中文部门名 URL 编码麻烦, 与其他筛选参数一致, 前端构造简单。

## ADR-4: 前端下钻优先用 Modal 保留独立路由

项目/人员下钻默认用 Modal, 同时保留 `/projects/:name` 路由支持深层链接。
理由: Modal 不丢失筛选状态和滚动位置, 独立路由满足分享链接需求。

## 数据导入设计规则

- 每月全量替换: 导入脚本先 DROP TABLE 再 CREATE, 然后 INSERT
- 姓名匹配策略: 精确匹配 -> 去 `_sz` 后缀匹配 -> 标记为"外部人力资源"
- 导入用 pandas 读 Excel + SQLModel 写 SQLite, 离线操作不用 async

## v2 新增决策(2026-07-18)

### ADR-6: 应有产能预计算落库

应有产能(每人每月)在导入脚本阶段预计算, 存入 `monthly_capacity` 表; 查询时直接 JOIN 读表, 不重复计算。
理由: 数据量极小(194人x6月 ~=1,200条), 预计算<2s; 中间值(work_days/in_service_days)存表可溯源。

### ADR-7: 项目分类建独立表

新增 `project_categories` 表存储三级分类(13细分->6分类->3大类), 替代 v1 的"不建项目表"决策。
理由: v2 需求层级映射, 必须结构化; 导入时匹配固化到 work_hours.category_id, 避免查询时做语义匹配。

### ADR-8: 节假日建独立表

新增 `holiday_calendar` 表存储假期+补班日期, 不硬编码。
理由: 可扩展(按年追加), 可溯源; 表仅~10行。

### ADR-9: 人名匹配: 工号优先

工时明细匹配花名册: 优先工号 -> 工号为空时去 `_sz` 后缀按姓名 -> 失败则不关联。
理由: 花名册有重名(陈鹏x2)需工号区分, 外包13人含 `_sz` 后缀。

### ADR-10: 项目名语义匹配"去季度前缀"

工时明细项目名去 Q1/Q2/Q3/2025Q4 前缀后, 与清单项目名做包含匹配; 31个未匹配项目归入"未分类"。
理由: 工时项目名含季度前缀, 清单不含; 匹配需灵活, 不能简单 equal。

**Why:** v2 核心增量是应有产能+项目分类, 设计时权衡了预计算 vs 实时计算、建表 vs 不建表、硬编码 vs 灵活存储。
**How to apply:** 当面对同类型"多数据源导入 + 预计算 + 多维分析"项目时, 优先复用预计算落库(ADR-6)、独立表建分类(ADR-7)、独立表建日历(ADR-8)、工号优先匹配(ADR-9)等模式。
