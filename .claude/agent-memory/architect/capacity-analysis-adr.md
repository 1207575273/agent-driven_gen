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

**Why:** 这些决策在产能分析场景中经过权衡, 后续类似"从 Excel 导入 + 聚合分析看板"项目可直接复用。
**How to apply:** 当面对同类型项目(数据导入 + 多维度聚合看板)时, 先检查是否可复用上述决策; 若数据量变大或需求变复杂, ADR-1/ADR-2 可能需要重新评估。
