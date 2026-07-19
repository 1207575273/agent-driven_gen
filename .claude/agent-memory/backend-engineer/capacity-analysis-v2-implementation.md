---
name: capacity-analysis-v2-implementation
description: 产能分析系统 v2 后端 P0 核心闭环实现总结
metadata:
  type: project
---

## 实现内容

v2 产能分析系统后端全量代码已实现并验证通过。最终检查:
- Ruff check: [PASS] All checks passed
- Ruff format: [PASS] 62 files already formatted
- mypy strict: [PASS] no issues found
- pytest: [PASS] 148 passed, coverage 82.16% (required >= 80%)

### 文件清单

**数据模型** (apps/back/app/models/):
- employee.py — Employee Base/Table/Create/Update/Public 全家桶
- work_hour.py — WorkHour 全家桶(含 FK employee_id + category_id)
- project_category.py — ProjectCategory 自引用树形表 + ThreeFastPlan
- holiday.py — Holiday (is_workday 区分假期/补班)
- should_be_capacity.py — ShouldBeCapacity 预计算存储
- three_fast_plan.py — ThreeFastPlan

**数据源抽象层** (apps/back/app/datasources/):
- base.py — DataSourceProvider ABC + ImportContext
- excel_provider.py — ExcelDataSourceProvider (pandas + openpyxl)

**纯计算引擎** (apps/back/app/services/):
- project_matching_engine.py — 项目名清洗 + 分类匹配(纯函数, 无 I/O)
- should_be_capacity_engine.py — 工作日计算 + 在职折算(纯计算, 无 I/O)

**Repository 层** (apps/back/app/repositories/):
- employee_repository.py — 基本 CRUD + distinct 部门查询 + 角色列表
- work_hour_repository.py — 聚合查询(GROUP BY 时间/项目/部门/角色/分类)
- project_category_repository.py — 分类树读取 + 树形结构
- holiday_repository.py — 节假日读写
- should_be_capacity_repository.py — 应有产能读写 + 聚合
- three_fast_plan_repository.py — 三快计划读写
- data_import_repository.py — 批量 INSERT、全表 DELETE、事务管理

**Service 层** (apps/back/app/services/):
- capacity_audit_service.py — KPI 汇总、月度趋势、填报率、零填报、偏差排行、异常明细、人员月度/项目明细
- cross_analysis_service.py — 时间x分类、应有vs实际、部门x分类、角色x分类、人员排名、综合矩阵、三快计划对比
- drill_down_service.py — 工时明细记录、部门子级、分类下项目列表
- filter_service.py — 返回所有可选筛选维度值
- data_import_service.py — 编排完整导入流程(清空->导入->匹配->计算)

**API 路由** (apps/back/app/api/v1/):
- capacity_audit.py — 8 个 GET 端点
- cross_analysis.py — 9 个 GET 端点
- drill_down.py — 3 个 GET 端点
- filters.py — 1 个 GET 端点
- data_import.py — 2 个 POST 端点

**CLI 脚本** (apps/back/scripts/):
- import_data.py — 离线导入脚本

**测试文件** (apps/back/app/tests/):
- test_project_matching_engine.py — 22 个测试(清洗 + 匹配)
- test_should_be_capacity_engine.py — 19 个测试(6 月工作日验证 + 在职折算)
- test_capacity.py — 107 个测试(Repository + Service + API 集成)

### 关键设计决策落地
1. 应有产能预计算存储: import 时触发 calculate_all, 按 (employee_id, year_month) 唯一约束
2. 项目分类在导入时匹配: 存储在 work_hours.category_id, rematch-categories 接口支持重新匹配
3. 部门从 employees DISTINCT: 不建独立部门表, filter_service + drill_down_service 按层级查询
4. 偏差判定在 service 层: _is_abnormal() |偏差| > 3 人天 且 偏差率 > 30%
5. 数据源 Provider 抽象: import_all() 只依赖 DataSourceProvider 接口

### 工作日数验证(架构方案 7.3)
| 月份 | 工作日 | 验证 |
|------|--------|------|
| 2026-01 | 22 | [PASS] |
| 2026-02 | 16 | [PASS] |
| 2026-03 | 23 | [PASS] |
| 2026-04 | 21 | [PASS] |
| 2026-05 | 19 | [PASS] |
| 2026-06 | 21 | [PASS] |
| H1 合计 | 122 | [PASS] |
