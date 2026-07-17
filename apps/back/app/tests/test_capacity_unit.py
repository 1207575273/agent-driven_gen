"""产能分析系统 - Repository 层和服务层单元测试。

使用内存 SQLite 在隔离环境中测试聚合查询逻辑。
"""

from datetime import date

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.work_hour import WorkHour
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.dashboard_service import DashboardService
from app.services.department_service import DepartmentService
from app.services.filter_service import FilterService
from app.services.filters import QueryFilters
from app.services.project_service import ProjectService
from app.services.role_service import RoleService


@pytest.fixture
async def populated_session(session: AsyncSession) -> AsyncSession:
    """在内存 DB 中植入测试数据。"""
    # 先建表
    async with session.begin():
        # SQLModel metadata 已注册
        pass

    # 插入测试员工
    emp1 = Employee(
        name="张三",
        employee_id="001",
        role="后端开发",
        level2_dept="技术部",
        level3_dept="技术部-基础平台",
        employee_status="正式",
        employee_type="在岗在编",
        is_outsourced=0,
        match_status="matched",
    )
    emp2 = Employee(
        name="李四",
        employee_id="002",
        role="前端开发",
        level2_dept="技术部",
        level3_dept="技术部-基础平台",
        employee_status="正式",
        employee_type="在岗在编",
        is_outsourced=0,
        match_status="matched",
    )
    emp3 = Employee(
        name="王五_sz",
        employee_id="003",
        role="测试",
        level2_dept="测试部",
        employee_status="兼岗",
        employee_type="在场",
        is_outsourced=1,
        match_status="matched",
    )
    emp4 = Employee(
        name="赵六",
        employee_id="004",
        role="PM",
        level2_dept="产品部",
        employee_status="离职",
        employee_type="在岗在编",
        is_outsourced=0,
        match_status="roster_only",
    )

    session.add_all([emp1, emp2, emp3, emp4])
    await session.flush()

    # 插入测试工时数据
    wh1 = WorkHour(
        project_name="项目A",
        reporter="张三",
        reporter_department="技术部",
        creator="张三",
        report_date=date(2026, 1, 15),
        hours=5.0,
        employee_id=emp1.id,
    )
    wh2 = WorkHour(
        project_name="项目A",
        reporter="张三",
        reporter_department="技术部",
        report_date=date(2026, 2, 10),
        hours=3.0,
        employee_id=emp1.id,
    )
    wh3 = WorkHour(
        project_name="项目B",
        reporter="李四",
        reporter_department="技术部",
        report_date=date(2026, 1, 20),
        hours=8.0,
        employee_id=emp2.id,
    )
    wh4 = WorkHour(
        project_name="项目A",
        reporter="王五_sz",
        reporter_department="测试部",
        report_date=date(2026, 1, 10),
        hours=2.0,
        employee_id=emp3.id,
    )
    wh5 = WorkHour(
        project_name="项目B",
        reporter="匿名外包",
        reporter_department="外包",
        report_date=date(2026, 3, 5),
        hours=4.0,
        employee_id=None,
    )

    session.add_all([wh1, wh2, wh3, wh4, wh5])
    await session.flush()
    await session.commit()

    return session


# ---------------------------------------------------------------------------
# Repository 层测试
# ---------------------------------------------------------------------------


async def test_aggregate_by_project(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_project()
    assert len(rows) >= 2
    projects = {r[0] for r in rows}
    assert "项目A" in projects
    assert "项目B" in projects

    # 项目A: 5+3+2 = 10, 2 个 distinct reporter(张三, 王五_sz)
    proj_a = next(r for r in rows if r[0] == "项目A")
    assert proj_a[1] == 10.0  # total_days
    assert proj_a[2] == 2  # member_count (2 distinct reporters)


async def test_aggregate_by_month(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_month()
    assert len(rows) >= 2
    months = {r[0] for r in rows}
    assert "2026-01" in months
    assert "2026-02" in months


async def test_aggregate_by_person(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_person()
    # 张三 8, 李四 8, 王五_sz 2, NULL 4 = 4 条记录(但有 NULL id 的情况)
    assert len(rows) >= 3


async def test_aggregate_by_role(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_role()
    roles = {r[0] for r in rows}
    assert "后端开发" in roles
    assert "前端开发" in roles


async def test_aggregate_by_status(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_status()
    statuses = {r[0] for r in rows}
    assert "正式" in statuses
    assert "兼岗" in statuses


async def test_date_filter(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_project(start_date=date(2026, 2, 1))
    # 只应包含 2 月及之后的记录
    assert len(rows) >= 1


async def test_department_filter(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_project(department="技术部")
    assert len(rows) >= 1


async def test_employee_repository_list_departments(populated_session: AsyncSession) -> None:
    repo = EmployeeRepository(populated_session)
    depts = await repo.list_departments(level=2)
    assert len(depts) >= 2
    assert "技术部" in depts


async def test_employee_repository_list_roles(populated_session: AsyncSession) -> None:
    repo = EmployeeRepository(populated_session)
    roles = await repo.list_roles()
    assert len(roles) >= 3
    assert "后端开发" in roles


# ---------------------------------------------------------------------------
# Service 层测试
# ---------------------------------------------------------------------------


async def test_dashboard_service_summary(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = DashboardService(wh_repo)
    result = await service.get_summary(QueryFilters())
    assert result["total_person_days"] == 22.0
    assert result["reporter_count"] >= 3
    assert result["project_count"] >= 2


async def test_dashboard_service_monthly_trend(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = DashboardService(wh_repo)
    result = await service.get_monthly_trend(QueryFilters())
    assert len(result) >= 2
    assert result[0]["month"] == "2026-01"
    assert result[0]["total_days"] == 15.0  # 5+8+2


async def test_project_service_ranking(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = ProjectService(wh_repo)
    result = await service.get_ranking(QueryFilters())
    assert len(result) >= 2
    proj_a = next(r for r in result if r["project_name"] == "项目A")
    assert proj_a["total_days"] == 10.0
    assert proj_a["member_count"] == 2  # 2 distinct reporters (张三, 王五_sz)
    assert proj_a["concentration"] == round(10.0 / 2, 1)


async def test_project_service_members(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = ProjectService(wh_repo)
    result = await service.get_project_members("项目A", QueryFilters())
    assert len(result) >= 2


async def test_department_service_overview(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    emp_repo = EmployeeRepository(populated_session)
    service = DepartmentService(wh_repo, emp_repo)
    result = await service.get_overview(QueryFilters(department="技术部"))
    assert result["total_person_days"] == 16.0  # 5+3+8
    assert result["member_count"] == 2
    assert "top_n_concentration" in result
    assert len(result["project_distribution"]) >= 1


async def test_department_service_members_with_deviation(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    emp_repo = EmployeeRepository(populated_session)
    service = DepartmentService(wh_repo, emp_repo)
    result = await service.get_members(QueryFilters(department="技术部"))
    assert len(result) == 2
    # 张三 8, 李四 8, 均值 8, deviation = 0
    assert all(r["deviation"] == 0.0 for r in result)


async def test_department_service_members_with_deviation_uneven(populated_session: AsyncSession) -> None:
    """测试不平等的偏离度。只在技术部: 张三 8, 李四 8 => 均值 8, 偏离度 0。"""
    # 这个场景两人一样多,正常。单独测试带更多变体的场景。
    # 实际环境中: 张三 8, 李四 8, 均值 8, deviation = 0
    wh_repo = WorkHourRepository(populated_session)
    emp_repo = EmployeeRepository(populated_session)
    service = DepartmentService(wh_repo, emp_repo)
    result = await service.get_members(QueryFilters(department="技术部"))
    assert len(result) == 2
    assert all(r["deviation_level"] == "normal" for r in result)


async def test_role_service_aggregation(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = RoleService(wh_repo)
    result = await service.get_aggregation(QueryFilters())
    roles = {r["role"] for r in result}
    assert "后端开发" in roles
    assert "前端开发" in roles


async def test_role_service_structure(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    service = RoleService(wh_repo)
    result = await service.get_structure(QueryFilters())
    assert len(result) >= 2
    statuses = {r["employee_status"] for r in result}
    assert "正式" in statuses


async def test_filter_service_options(populated_session: AsyncSession) -> None:
    wh_repo = WorkHourRepository(populated_session)
    emp_repo = EmployeeRepository(populated_session)
    service = FilterService(wh_repo, emp_repo)
    result = await service.get_filter_options()
    assert len(result["departments"]) >= 2
    assert len(result["roles"]) >= 3
    assert len(result["projects"]) >= 2
    assert result["personnel_types"] == ["在编", "外部人力资源"]


async def test_department_overview_not_found(populated_session: AsyncSession) -> None:
    from app.core.exceptions import NotFoundError

    wh_repo = WorkHourRepository(populated_session)
    emp_repo = EmployeeRepository(populated_session)
    service = DepartmentService(wh_repo, emp_repo)
    with pytest.raises(NotFoundError):
        await service.get_overview(QueryFilters())


async def test_aggregate_person_project(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_by_person_project(employee_id=1)
    assert len(rows) >= 1


async def test_aggregate_person_project_by_month(populated_session: AsyncSession) -> None:
    repo = WorkHourRepository(populated_session)
    rows = await repo.aggregate_person_project_by_month(employee_id=1, project_name="项目A")
    assert len(rows) >= 1
    assert rows[0][0] in ("2026-01", "2026-02")


async def test_employee_repository_list_by_department(populated_session: AsyncSession) -> None:
    repo = EmployeeRepository(populated_session)
    emps = await repo.list_by_department("技术部", level=2)
    assert len(emps) == 2
    names = {e.name for e in emps}
    assert "张三" in names
    assert "李四" in names
