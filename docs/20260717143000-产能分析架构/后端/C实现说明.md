# 产能分析系统 - 后端实现说明

## 分层落地

### Models: `app/models/`

| 文件 | 实体 | 对应 Excel |
|------|------|------------|
| `employee.py` | Employee(5 类: Base/Table/Create/Update/Public) | 完整花名册 |
| `work_hour.py` | WorkHour(5 类) | 工时明细 |

关键设计:
- Employee 包含 `is_outsourced`(=0/1) 和 `match_status`(roster_only/matched) 两个状态字段,由 import 脚本计算。
- WorkHour.employee_id FK 到 employees.id, 允许 NULL(无匹配工时归为"其他")。
- 索引覆盖所有常用筛选列: name/level2_dept/role/employee_type/employee_status/is_outsourced/match_status / project_name/reporter/report_date/employee_id。

### Repositories: `app/repositories/`

| 文件 | 关键方法 | 说明 |
|------|----------|------|
| `work_hour_repository.py` | 9 种聚合查询 + 筛选链 | 核心查询层 |
| `employee_repository.py` | list_departments/list_roles/list_personnel_types/list_employee_statuses/list_by_department/get/list_all | 筛选器选项数据 |

**常量**:
- `DEPT_COL_NAMES = {2: "level2_dept", 3: "level3_dept"}` — 部门层级 -> 列名映射
- `PERSONNEL_TYPES = ["在编", "外部人力资源"]` — 写死在 repo,因为不随数据变化

**筛选链**: 所有聚合方法以 `QueryFilters` 参数共享 `_apply_common()` 辅助方法,按需 JOIN employees 表。

### Services: `app/services/`

| 文件 | 职责 |
|------|------|
| `filters.py` | QueryFilters 数据类(纯数据结构,6 个可选筛选字段) |
| `dashboard_service.py` | 总人天/填报人数/项目数/部门数 + 月度趋势 |
| `project_service.py` | 项目排行榜(含集中度) + 人员下钻 + 项目月度趋势 |
| `department_service.py` | 部门概况(含项目分布、Top-N 集中度) + 人员排行榜(含偏离度) + 个人项目详情 |
| `role_service.py` | 角色聚合 + 部门分布 + 人力结构(按员工状态) |
| `filter_service.py` | 所有可用筛选选项(部门/角色/项目/日期范围等) |

**关键算法**:
- **偏离度**: `(个人人天 - 均值) / 均值`,阈值 0.5(normal)/1.0(warning),>1.0 = severe
- **集中度**: Top-3 项目人天 / 部门总人天
- 统计口径: `total_person_days = sum(hours)` (原始工时即为人天,Excel 数据已折算)

### Routes: `app/api/v1/`

| 文件 | 端点(GET) | 说明 |
|------|-----------|------|
| `dashboard.py` | `/dashboard/summary` `/dashboard/monthly-trend` | 仪表盘 |
| `projects.py` | `/projects/ranking` `/projects/{name}/members` `/projects/{name}/monthly-trend` | 项目维度 |
| `departments.py` | `/departments/overview` `/departments/members` `/departments/members/{id}/projects` | 部门维度 |
| `roles.py` | `/roles/aggregation` `/roles/structure` | 角色维度 |
| `filters.py` | `/filters/options` | 筛选选项 |

所有查询参数使用 `Annotated[type, Query()]` 避免 ruff B008。

### DI: `app/api/deps.py`

```text
session -> WorkHourRepository -> DashboardService/ProjectService/RoleService
session -> EmployeeRepository -> DepartmentService/FilterService

链上只有 session 是真实 AsyncSession,
其余 Depends 层层装配,路由只拿 Service 实例。
```

### 数据导入: `scripts/import_data.py`

独立 CLI(不依赖 FastAPI),用 SQLAlchemy Core 直接写库,按 reporter 姓名匹配花名册:
1. 精确匹配
2. 去 `_sz` 后缀匹配 -> 标记为外包(`is_outsourced=1`)
3. 无匹配 -> employee_id=NULL(计入"人员类型=外部人力资源"筛选项)

---

## 接口统计

| 维度 | 端点数 |
|------|--------|
| Dashboard | 2 |
| Projects | 3 |
| Departments | 3 |
| Roles | 2 |
| Filters | 1 |
| **合计** | **11** |

全部 GET,无 POST 端点在 P0。

---

## 测试

- **覆盖率**: 89.74% (>80% 阈值)
- **测试文件**: `test_capacity_unit.py`(23 个单元测试,内存 SQLite + 4 员工 + 5 工时)
- **覆盖范围**: Repository 聚合查询(9 个方法) + Service 层所有服务类
- **未覆盖**: 路由层薄控制器(不做独立测试,走集成测试),部分异常分支

---

## 关键取舍

1. **统计口径**: person_days = sum(hours),不除以 8。原始 Excel 数据工时字段实为人天值。
2. **外部人力**: 固定返回 `["在编", "外部人力资源"]`,前者的子查询排除 `is_outsourced=1`,后者包含外包+匿名(employee_id IS NULL)。
3. **偏离度**: 在 service 层计算(Python 而非 SQL),含均值/分子/分母,便于排查。
4. **部门筛选**: department + department_level 组合,默认 level=2(二级部门)。
5. **mypy strict + SQLModel**: 58 行 `Any` 类型 + 4 处 `# type: ignore` 的最小子集,核心在 `select()` overload 与 InstrumentedAttribute 的静态类型摩擦。
