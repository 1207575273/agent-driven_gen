"""产能分析系统集成测试: Repository + Service + Route(http client)。

每个测试通过 client 夹具走完整请求链(内存 SQLite)。
"""

from collections.abc import Iterator
from datetime import date

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.holiday import Holiday
from app.models.project_category import ProjectCategory
from app.models.should_be_capacity import ShouldBeCapacity
from app.models.three_fast_plan import ThreeFastPlan
from app.models.work_hour import WorkHour

# ==============================================================================
# Fixtures: 预置基础数据
# ==============================================================================


async def _seed_employees(session: AsyncSession) -> list[Employee]:
    emps = [
        Employee(
            name="张三",
            employee_id="EMP001",
            level1_dept="技术部",
            level2_dept="基础平台组",
            level3_dept="后端组",
            role="后端开发",
            employee_status="在职",
            is_excluded=False,
            entry_date=date(2025, 1, 1),
        ),
        Employee(
            name="李四",
            employee_id="EMP002",
            level1_dept="技术部",
            level2_dept="产品组",
            level3_dept="产品一组",
            role="产品经理",
            employee_status="在职",
            is_excluded=False,
            entry_date=date(2025, 1, 1),
        ),
        Employee(
            name="王五",
            employee_id=None,
            level1_dept="测试部",
            level2_dept="质量组",
            level3_dept="自动化",
            role="测试",
            employee_status="在职",
            is_excluded=False,
            entry_date=date(2025, 6, 1),
        ),
        Employee(
            name="勉填人",
            employee_id="EMP_EXC",
            level1_dept="技术部",
            level2_dept="基础平台组",
            role="后端开发",
            employee_status="在职",
            is_excluded=True,
            fill_note="勉填",
        ),
        Employee(
            name="已离职",
            employee_id="EMP_LFT",
            level1_dept="技术部",
            level2_dept="基础平台组",
            role="后端开发",
            employee_status="离职",
            is_excluded=False,
            leave_date=date(2025, 12, 31),
        ),
        Employee(
            name="待入职",
            employee_id="EMP_PEND",
            level1_dept="技术部",
            level2_dept="基础平台组",
            role="后端开发",
            employee_status="待入职",
            is_excluded=False,
            entry_date=date(2026, 7, 1),
        ),
    ]
    session.add_all(emps)
    await session.flush()
    return emps


async def _seed_categories(session: AsyncSession) -> list[ProjectCategory]:
    cats = [
        # level 1
        ProjectCategory(id=1, category_name="三快类", category_level=1, parent_id=None, sort_order=1),
        ProjectCategory(id=2, category_name="研发类", category_level=1, parent_id=None, sort_order=2),
        ProjectCategory(id=3, category_name="周期类", category_level=1, parent_id=None, sort_order=3),
        # level 2
        ProjectCategory(id=4, category_name="快服务", category_level=2, parent_id=1, sort_order=1),
        ProjectCategory(id=5, category_name="快交付", category_level=2, parent_id=1, sort_order=2),
        ProjectCategory(id=6, category_name="创新专项", category_level=2, parent_id=2, sort_order=1),
        # level 3
        ProjectCategory(id=7, category_name="快服务迭代", category_level=3, parent_id=4, sort_order=1),
        ProjectCategory(id=8, category_name="快服务子专项", category_level=3, parent_id=4, sort_order=2),
        ProjectCategory(id=9, category_name="快交付迭代", category_level=3, parent_id=5, sort_order=1),
    ]
    session.add_all(cats)
    await session.flush()
    return cats


async def _seed_holidays(session: AsyncSession) -> None:
    """预置 2026-H1 假期和补班日(按架构方案 7.3 验证数字)。"""
    holidays = [
        # 春节放假 2/15-2/19 (5天), 补班 2/14
        Holiday(holiday_name="春节", holiday_date=date(2026, 2, 15), is_workday=False),
        Holiday(holiday_name="春节", holiday_date=date(2026, 2, 16), is_workday=False),
        Holiday(holiday_name="春节", holiday_date=date(2026, 2, 17), is_workday=False),
        Holiday(holiday_name="春节", holiday_date=date(2026, 2, 18), is_workday=False),
        Holiday(holiday_name="春节", holiday_date=date(2026, 2, 19), is_workday=False),
        Holiday(holiday_name="春节补班", holiday_date=date(2026, 2, 14), is_workday=True),
        # 3月补班 3/1
        Holiday(holiday_name="3月补班", holiday_date=date(2026, 3, 1), is_workday=True),
        # 清明 4/6 补休
        Holiday(holiday_name="清明", holiday_date=date(2026, 4, 6), is_workday=False),
        # 五一 5/1-5/3, 补班 5/9
        Holiday(holiday_name="五一", holiday_date=date(2026, 5, 1), is_workday=False),
        Holiday(holiday_name="五一", holiday_date=date(2026, 5, 2), is_workday=False),
        Holiday(holiday_name="五一", holiday_date=date(2026, 5, 3), is_workday=False),
        Holiday(holiday_name="五一补班", holiday_date=date(2026, 5, 9), is_workday=True),
        # 端午 6/19
        Holiday(holiday_name="端午", holiday_date=date(2026, 6, 19), is_workday=False),
    ]
    session.add_all(holidays)
    await session.flush()


async def _seed_work_hours(session: AsyncSession, employees: list[Employee]) -> None:
    """给在职员工(张三、李四、王五)添加 2026-01 到 2026-06 的工时记录。"""
    emp_map = {e.name: e for e in employees}
    wh_data: list[WorkHour] = []

    zhang = emp_map["张三"]
    li = emp_map["李四"]
    wang = emp_map["王五"]

    # 张三: 每月约 20 天, 项目: 快服务项目(分类7) 10天 + 快交付项目(分类9) 10天
    for m in range(1, 7):
        for d in range(1, 21):
            if d <= 10:
                wh_data.append(
                    WorkHour(
                        project_name="快服务项目",
                        reporter="张三",
                        report_date=date(2026, m, d),
                        hours=1.0,
                        employee_id=zhang.id,
                        matched_project_name="快服务项目",
                        category_id=7,
                    )
                )
            else:
                wh_data.append(
                    WorkHour(
                        project_name="快交付项目",
                        reporter="张三",
                        report_date=date(2026, m, d),
                        hours=1.0,
                        employee_id=zhang.id,
                        matched_project_name="快交付项目",
                        category_id=9,
                    )
                )

    # 李四: 每月约 18 天, 全部快服务项目
    for m in range(1, 7):
        for d in range(1, 19):
            wh_data.append(
                WorkHour(
                    project_name="快服务项目",
                    reporter="李四",
                    report_date=date(2026, m, d),
                    hours=1.0,
                    employee_id=li.id,
                    matched_project_name="快服务项目",
                    category_id=7,
                )
            )

    # 王五: 每月约 15 天, 无特定项目分类
    for m in range(1, 7):
        for d in range(1, 16):
            wh_data.append(
                WorkHour(
                    project_name="日常运营",
                    reporter="王五",
                    report_date=date(2026, m, d),
                    hours=1.0,
                    employee_id=wang.id,
                    matched_project_name="日常运营",
                    category_id=9,
                )
            )

    session.add_all(wh_data)
    await session.flush()


async def _seed_should_be_capacity(session: AsyncSession, employees: list[Employee]) -> None:
    """预计算应有产能(按架构方案 7.3 每月工作日数)。"""
    month_days = {
        "2026-01": (22, 22),
        "2026-02": (16, 16),
        "2026-03": (23, 23),
        "2026-04": (21, 21),
        "2026-05": (19, 19),
        "2026-06": (21, 21),
    }
    emp_map = {e.name: e for e in employees}
    active_names = ["张三", "李四", "王五"]

    for name in active_names:
        emp = emp_map[name]
        for ym, (twd, awd) in month_days.items():
            sbc = ShouldBeCapacity(
                employee_id=emp.id,  # type: ignore[arg-type]
                year_month=ym,
                total_working_days=twd,
                active_working_days=awd,
                capacity_days=float(awd),
            )
            session.add(sbc)
    await session.flush()


async def _seed_three_fast_plans(session: AsyncSession) -> None:
    plans = [
        ThreeFastPlan(plan_quarter="2026-01", category_id=4, plan_days=600.0),  # 快服务
        ThreeFastPlan(plan_quarter="2026-01", category_id=5, plan_days=500.0),  # 快交付
        ThreeFastPlan(plan_quarter="2026-04", category_id=4, plan_days=650.0),
    ]
    session.add_all(plans)
    await session.flush()


# ==============================================================================
# Repository 层测试(直接 session)
# ==============================================================================


class TestEmployeeRepository:
    async def test_list_all(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emps = await repo.list_all()
        assert len(emps) == 6

    async def test_list_active_normal_excludes_excluded_and_left(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emps = await repo.list_active_normal()
        # 排除: 勉填人(is_excluded), 已离职(status=离职) -> 保留 4 人(张三/李四/王五/待入职)
        # 注意: 待入职人员在应有产能计算层过滤(capacity_days=0), Repository 不过滤
        assert len(emps) == 4
        names = {e.name for e in emps}
        assert "张三" in names
        assert "李四" in names
        assert "王五" in names

    async def test_list_departments(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        depts = await repo.list_departments(2)
        assert len(depts) >= 2
        assert "基础平台组" in depts or "产品组" in depts

    async def test_list_roles(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        roles = await repo.list_roles()
        assert "后端开发" in roles

    async def test_get_by_employee_id_str(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emp = await repo.get_by_employee_id_str("EMP001")
        assert emp is not None
        assert emp.name == "张三"

    async def test_get_by_name(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emp = await repo.get_by_name("李四")
        assert emp is not None
        assert emp.employee_id == "EMP002"


class TestWorkHourRepository:
    async def test_aggregate_by_time_and_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_time_and_category(date(2026, 1, 1), date(2026, 1, 31), 1)
        assert len(rows) > 0

    async def test_aggregate_by_dept_and_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_dept_and_category(date(2026, 1, 1), date(2026, 6, 30), 2)
        assert len(rows) > 0

    async def test_get_records(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        records = await repo.get_records(employee_id=emps[0].id)
        assert len(records) > 0
        assert all(r.employee_id == emps[0].id for r in records)


class TestProjectCategoryRepository:
    async def test_list_all(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        cats = await repo.list_all()
        assert len(cats) == 9

    async def test_get_by_level(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        majors = await repo.get_by_level(1)
        assert len(majors) == 3

    async def test_get_by_parent(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        children = await repo.get_by_parent(1)
        assert len(children) == 2

    async def test_get_major_categories(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        majors = await repo.get_major_categories()
        assert len(majors) == 3
        # 三快类 children
        for m in majors:
            if m["category_name"] == "三快类":
                children = m.get("children", [])
                assert isinstance(children, list)
                assert len(children) == 2


class TestHolidayRepository:
    async def test_list_all(self, session: AsyncSession) -> None:
        await _seed_holidays(session)
        from app.repositories.holiday_repository import HolidayRepository

        repo = HolidayRepository(session)
        holidays = await repo.list_all()
        assert len(holidays) == 13

    async def test_get_by_year_month(self, session: AsyncSession) -> None:
        await _seed_holidays(session)
        from app.repositories.holiday_repository import HolidayRepository

        repo = HolidayRepository(session)
        feb_holidays = await repo.get_by_year_month("2026-02")
        assert len(feb_holidays) == 6  # 5 假期 + 1 补班


class TestShouldBeCapacityRepository:
    async def test_list_by_employee(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        zhang = next(e for e in emps if e.name == "张三")
        records = await repo.list_by_employee(zhang.id)  # type: ignore[arg-type]
        assert len(records) == 6

    async def test_aggregate_by_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        rows = await repo.aggregate_by_month(["2026-01", "2026-02"])
        assert len(rows) == 2

    async def test_get_total_by_period(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        total = await repo.get_total_by_period(["2026-01", "2026-02", "2026-03"])
        should_be = float(str(total.get("should_be_days", 0)))
        assert should_be > 0


class TestThreeFastPlanRepository:
    async def test_list_all(self, session: AsyncSession) -> None:
        await _seed_three_fast_plans(session)
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository

        repo = ThreeFastPlanRepository(session)
        plans = await repo.list_all()
        assert len(plans) == 3

    async def test_get_by_quarter(self, session: AsyncSession) -> None:
        await _seed_three_fast_plans(session)
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository

        repo = ThreeFastPlanRepository(session)
        q1_plans = await repo.get_by_quarter("2026-01")
        assert len(q1_plans) > 0


# ==============================================================================
# Service 层测试(通过 repo 走真实 session)
# ==============================================================================


class TestCapacityAuditService:
    async def test_get_summary(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_summary(time_period="2026-H1")
        assert isinstance(result, dict)
        assert float(str(result["should_be_days"])) > 0
        assert float(str(result["actual_days"])) > 0
        assert float(str(result["fill_rate"])) >= 0

    async def test_get_monthly_trend(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_monthly_trend(time_period="2026-H1")
        assert len(result) == 6
        for item in result:
            assert "month" in item
            assert float(str(item["should_be_days"])) >= 0

    async def test_get_deviation_ranking(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_deviation_ranking(time_period="2026-H1")
        assert len(result) > 0

    async def test_get_person_monthly(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        zhang = next(e for e in emps if e.name == "张三")
        result = await svc.get_person_monthly(zhang.id)  # type: ignore[arg-type]
        assert result["employee_id"] == zhang.id
        monthly = result["monthly_data"]
        assert isinstance(monthly, list)
        assert len(monthly) == 6


class TestCrossAnalysisService:
    async def test_get_time_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_time_category(time_period="2026-H1")
        assert len(result) > 0

    async def test_get_should_vs_actual(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_should_vs_actual(time_period="2026-H1")
        assert len(result) == 6

    async def test_get_dept_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_dept_category()
        assert len(result) > 0

    async def test_get_dept_category_matrix(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_dept_category_matrix()
        assert "depts" in result
        assert "categories" in result
        assert "matrix" in result

    async def test_get_role_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_role_category()
        assert len(result) > 0

    async def test_get_person_ranking(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_person_ranking()
        assert len(result) > 0

    async def test_get_three_fast_comparison(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        await _seed_three_fast_plans(session)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_three_fast_comparison()
        assert len(result) == 3


class TestDrillDownService:
    async def test_get_records(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        zhang = next(e for e in emps if e.name == "张三")
        result = await svc.get_records(employee_id=zhang.id, limit=10)
        assert len(result) > 0
        assert len(result) <= 10

    async def test_get_dept_children(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_dept_children(time_period="2026-H1", parent_dept="技术部", dept_level=2)
        assert len(result) > 0

    async def test_get_category_projects(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_category_projects(time_period="2026-H1", category_id=7)
        assert len(result) > 0


class TestFilterService:
    async def test_get_options(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        await _seed_categories(session)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.services.filter_service import FilterService

        svc = FilterService(EmployeeRepository(session), ProjectCategoryRepository(session))
        result = await svc.get_options()
        assert "time_range" in result
        assert "departments" in result
        assert "roles" in result
        assert "categories" in result


# ==============================================================================
# API 路由层测试(http client, 走完整请求链)
# ==============================================================================


async def _seed_all(session: AsyncSession) -> tuple[list[Employee], list[ProjectCategory]]:
    emps = await _seed_employees(session)
    cats = await _seed_categories(session)
    await _seed_holidays(session)
    await _seed_work_hours(session, emps)
    await _seed_should_be_capacity(session, emps)
    await _seed_three_fast_plans(session)
    await session.flush()
    return emps, cats


@pytest.mark.anyio
async def test_api_filters_options(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/filters/options")
    assert resp.status_code == 200
    data = resp.json()
    assert "time_range" in data


@pytest.mark.anyio
async def test_api_capacity_audit_summary(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/summary?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert "should_be_days" in data
    assert "actual_days" in data


@pytest.mark.anyio
async def test_api_capacity_audit_monthly_trend(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/monthly-trend?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 6


@pytest.mark.anyio
async def test_api_capacity_audit_department_fill_rate(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/department-fill-rate?dept_level=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_capacity_audit_zero_filling(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/zero-filling?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_capacity_audit_deviation_ranking(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/deviation-ranking?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_capacity_audit_abnormal_detail(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/capacity-audit/abnormal-detail?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_capacity_audit_person_monthly(client: AsyncClient, session: AsyncSession) -> None:
    emps, _cats = await _seed_all(session)
    zhang = next(e for e in emps if e.name == "张三")
    resp = await client.get(f"/api/v1/capacity-audit/person-monthly?employee_id={zhang.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == zhang.id
    assert "monthly_data" in data


@pytest.mark.anyio
async def test_api_capacity_audit_person_projects(client: AsyncClient, session: AsyncSession) -> None:
    emps, _cats = await _seed_all(session)
    zhang = next(e for e in emps if e.name == "张三")
    resp = await client.get(f"/api/v1/capacity-audit/person-projects?employee_id={zhang.id}&time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_time_category(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/time-category?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_should_vs_actual(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/should-vs-actual?time_period=2026-H1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_dept_category(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/dept-category")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_dept_category_matrix(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/dept-category-matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert "depts" in data
    assert "matrix" in data


@pytest.mark.anyio
async def test_api_cross_analysis_role_category(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/role-category")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_role_monthly_trend(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/role-monthly-trend?role=后端开发")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_person_ranking(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/person-ranking")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_three_fast_comparison(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/three-fast-comparison")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_cross_analysis_matrix(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/cross-analysis/matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


@pytest.mark.anyio
async def test_api_drill_down_records(client: AsyncClient, session: AsyncSession) -> None:
    emps, _cats = await _seed_all(session)
    zhang = next(e for e in emps if e.name == "张三")
    resp = await client.get(f"/api/v1/drill-down/records?employee_id={zhang.id}&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) <= 5


@pytest.mark.anyio
async def test_api_drill_down_dept_children(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/drill-down/dept-children?parent_dept=&dept_level=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_api_drill_down_category_projects(client: AsyncClient, session: AsyncSession) -> None:
    await _seed_all(session)
    resp = await client.get("/api/v1/drill-down/category-projects?category_id=7")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


class TestDataImportService:
    async def test_import_all(self, session: AsyncSession) -> None:
        """测试 DataImportService 完整导入流程。"""
        from datetime import date as dt_date

        from app.datasources.base import DataSourceProvider
        from app.repositories.data_import_repository import DataImportRepository
        from app.services.data_import_service import DataImportService

        class FakeProvider(DataSourceProvider):
            def provide_employees(self) -> Iterator[dict[str, object]]:
                yield {
                    "name": "测试员",
                    "employee_id": "T001",
                    "position": "开发",
                    "level1_dept": "技术部",
                    "level2_dept": "测试组",
                    "level3_dept": None,
                    "level4_dept": None,
                    "actual_team": None,
                    "role": "开发",
                    "employee_type": "正式",
                    "employee_status": "在职",
                    "position_type": "技术",
                    "entry_date": dt_date(2025, 1, 1),
                    "leave_date": None,
                    "fill_note": None,
                    "remarks": None,
                    "planned_project1": None,
                    "planned_project2": None,
                    "planned_project3": None,
                    "planned_project4": None,
                    "planned_project5": None,
                    "is_excluded": False,
                }

            def provide_work_hours(self) -> Iterator[dict[str, object]]:
                yield {
                    "project_name": "快服务项目",
                    "reporter": "测试员",
                    "reporter_department": "技术部",
                    "creator": None,
                    "report_date": dt_date(2026, 1, 5),
                    "hours": 1.0,
                    "description": "开发",
                }

            def provide_project_categories(self) -> list[dict[str, object]]:
                return [
                    {"category_name": "三快类", "category_level": 1, "parent_id": None, "sort_order": 1, "id": None},
                    {"category_name": "快服务", "category_level": 2, "parent_id": None, "sort_order": 1, "id": None},
                    {
                        "category_name": "快服务迭代",
                        "category_level": 3,
                        "parent_id": None,
                        "sort_order": 1,
                        "id": None,
                    },
                    {
                        "category_name": "快服务项目",
                        "category_level": 0,
                        "parent_id": None,
                        "sort_order": 0,
                        "id": None,
                    },
                ]

            def provide_holidays(self) -> list[dict[str, object]]:
                return [
                    {"holiday_name": "春节", "holiday_date": dt_date(2026, 2, 15), "is_workday": False},
                    {"holiday_name": "春节", "holiday_date": dt_date(2026, 2, 16), "is_workday": False},
                ]

            def provide_three_fast_plans(self) -> list[dict[str, object]]:
                return []

        repo = DataImportRepository(session)
        svc = DataImportService(repo)
        result = await svc.import_all(FakeProvider())

        assert result.get("success") is True
        stats = result.get("stats", {})
        assert isinstance(stats, dict)
        assert stats.get("employees_imported") == 1
        assert stats.get("work_hours_imported") == 1
        assert (stats.get("categories_imported") or 0) > 0

    async def test_rematch_categories(self, session: AsyncSession) -> None:
        """测试重新匹配分类(需要先有数据)。"""
        from datetime import date as dt_date

        from app.datasources.base import DataSourceProvider
        from app.repositories.data_import_repository import DataImportRepository
        from app.services.data_import_service import DataImportService

        class FakeProvider(DataSourceProvider):
            def provide_employees(self) -> Iterator[dict[str, object]]:
                yield {
                    "name": "测试员",
                    "employee_id": "T001",
                    "position": None,
                    "level1_dept": None,
                    "level2_dept": None,
                    "level3_dept": None,
                    "level4_dept": None,
                    "actual_team": None,
                    "role": None,
                    "employee_type": None,
                    "employee_status": "在职",
                    "position_type": None,
                    "entry_date": dt_date(2025, 1, 1),
                    "leave_date": None,
                    "fill_note": None,
                    "remarks": None,
                    "planned_project1": None,
                    "planned_project2": None,
                    "planned_project3": None,
                    "planned_project4": None,
                    "planned_project5": None,
                    "is_excluded": False,
                }

            def provide_work_hours(self) -> Iterator[dict[str, object]]:
                yield {
                    "project_name": "快服务迭代",
                    "reporter": "测试员",
                    "reporter_department": None,
                    "creator": None,
                    "report_date": dt_date(2026, 1, 5),
                    "hours": 1.0,
                    "description": None,
                }

            def provide_project_categories(self) -> list[dict[str, object]]:
                return [
                    {
                        "category_name": "快服务迭代",
                        "category_level": 3,
                        "parent_id": None,
                        "sort_order": 1,
                        "id": None,
                    }
                ]

            def provide_holidays(self) -> list[dict[str, object]]:
                return []

            def provide_three_fast_plans(self) -> list[dict[str, object]]:
                return []

        repo = DataImportRepository(session)
        svc = DataImportService(repo)
        await svc.import_all(FakeProvider())
        rematch_result = await svc.rematch_categories()
        assert rematch_result.get("success") is True


class TestDataSourceProvider:
    def test_base_abc_cannot_instantiate(self) -> None:
        from app.datasources.base import DataSourceProvider

        with pytest.raises(TypeError):
            DataSourceProvider()  # type: ignore[abstract]

    def test_import_context_defaults(self) -> None:
        from app.datasources.base import ImportContext

        ctx = ImportContext()
        assert ctx.stats == {}
        assert ctx.errors == []


class TestCapacityAuditHelpers:
    def test_is_abnormal(self) -> None:
        from app.services.capacity_audit_service import _is_abnormal

        # |偏差| > 3 且 偏差率 > 30%
        assert _is_abnormal(5.0, 10.0) is True  # 5/10 = 50%
        assert _is_abnormal(2.0, 10.0) is False  # |偏差| <= 3
        assert _is_abnormal(4.0, 20.0) is False  # 偏差率 20% <= 30%
        assert _is_abnormal(0.0, 10.0) is False
        assert _is_abnormal(5.0, 0.0) is False  # should_be=0

    def test_parse_year_months(self) -> None:
        from app.services.capacity_audit_service import _parse_year_months

        assert _parse_year_months(None) == ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
        assert len(_parse_year_months("2026-H1")) == 6
        assert _parse_year_months("2026-Q1") == ["2026-01", "2026-02", "2026-03"]
        assert _parse_year_months("2026-Q2") == ["2026-04", "2026-05", "2026-06"]
        assert _parse_year_months("2026-03") == ["2026-03"]

    def test_year_month_to_date_range(self) -> None:
        from app.services.capacity_audit_service import _year_month_to_date_range

        start, end = _year_month_to_date_range(["2026-01"])
        assert start == date(2026, 1, 1)
        assert end == date(2026, 1, 31)

        start, end = _year_month_to_date_range(["2026-01", "2026-03"])
        assert start == date(2026, 1, 1)
        assert end == date(2026, 3, 31)


# ==============================================================================
# 补充 Repository 覆盖(使用已有 seed 函数)
# ==============================================================================


class TestWorkHourRepositoryExtended:
    async def test_aggregate_by_role(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_role_and_category(date(2026, 1, 1), date(2026, 6, 30))
        assert len(rows) > 0

    async def test_aggregate_by_person(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_person_and_category(date(2026, 1, 1), date(2026, 6, 30))
        assert len(rows) > 0
        for r in rows:
            assert "employee_id" in r

    async def test_aggregate_by_person_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        zhang = next(e for e in emps if e.name == "张三")
        rows = await repo.aggregate_by_person_month(zhang.id, date(2026, 1, 1), date(2026, 6, 30))  # type: ignore[arg-type]
        assert len(rows) == 6

    async def test_rank_by_person(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.rank_by_person(date(2026, 1, 1), date(2026, 6, 30))
        assert len(rows) > 0

    async def test_aggregate_by_dept_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_dept_month(date(2026, 1, 1), date(2026, 6, 30), 2)
        assert len(rows) > 0

    async def test_aggregate_by_category_and_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_category_and_month(date(2026, 1, 1), date(2026, 6, 30), 1)
        assert len(rows) > 0

    async def test_get_projects_by_category(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.get_projects_by_category(7, date(2026, 1, 1), date(2026, 6, 30))
        assert len(rows) > 0

    async def test_get_person_projects(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        zhang = next(e for e in emps if e.name == "张三")
        rows = await repo.get_person_projects(zhang.id, date(2026, 1, 1), date(2026, 6, 30))  # type: ignore[arg-type]
        assert len(rows) > 0

    async def test_get_distinct_projects(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        projects = await repo.get_distinct_matched_projects()
        assert len(projects) > 0

    async def test_get_records_with_all_filters(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        records = await repo.get_records(
            employee_id=emps[0].id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            project_name="快服务项目",
            category_id=7,
            limit=10,
        )
        assert len(records) > 0

    async def test_aggregate_by_person_with_category(self, session: AsyncSession) -> None:
        """人员 x 分类交叉聚合。"""
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.work_hour_repository import WorkHourRepository

        repo = WorkHourRepository(session)
        rows = await repo.aggregate_by_person_with_category(
            date(2026, 1, 1), date(2026, 6, 30), 1
        )
        assert len(rows) > 0
        assert "category_distribution" in rows[0]
        assert "name" in rows[0]
        assert "total_days" in rows[0]


class TestHolidayRepositoryExtended:
    async def test_get_by_date(self, session: AsyncSession) -> None:
        await _seed_holidays(session)
        from app.repositories.holiday_repository import HolidayRepository

        repo = HolidayRepository(session)
        h = await repo.get_by_date(date(2026, 2, 15))
        assert h is not None
        assert h.holiday_name == "春节"

    async def test_get_holidays_by_month(self, session: AsyncSession) -> None:
        await _seed_holidays(session)
        from app.repositories.holiday_repository import HolidayRepository

        repo = HolidayRepository(session)
        holidays = await repo.get_holidays_by_month("2026-02")
        assert len(holidays) > 0
        for h in holidays:
            assert not h.is_workday

    async def test_get_supplements_by_month(self, session: AsyncSession) -> None:
        await _seed_holidays(session)
        from app.repositories.holiday_repository import HolidayRepository

        repo = HolidayRepository(session)
        supps = await repo.get_supplements_by_month("2026-02")
        assert len(supps) > 0
        for s in supps:
            assert s.is_workday


class TestThreeFastPlanRepositoryExtended:
    async def test_get_by_category(self, session: AsyncSession) -> None:
        await _seed_three_fast_plans(session)
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository

        repo = ThreeFastPlanRepository(session)
        plans = await repo.get_by_category(4)  # 快服务
        assert len(plans) > 0
        for p in plans:
            assert p.category_id == 4


class TestEmployeeRepositoryExtended:
    async def test_get_missing(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emp = await repo.get(9999)
        assert emp is None

    async def test_get_by_employee_id_str_missing(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emp = await repo.get_by_employee_id_str("NONEXIST")
        assert emp is None

    async def test_get_by_name_missing(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emp = await repo.get_by_name("不存在")
        assert emp is None

    async def test_list_by_department(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository

        repo = EmployeeRepository(session)
        emps = await repo.list_by_department(2, "基础平台组")
        assert len(emps) > 0
        for e in emps:
            assert e.level2_dept == "基础平台组"


class TestShouldBeCapacityRepositoryExtended:
    async def test_get_by_employee_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        zhang = next(e for e in emps if e.name == "张三")
        sbc = await repo.get_by_employee_month(zhang.id, "2026-01")  # type: ignore[arg-type]
        assert sbc is not None
        assert sbc.capacity_days == 22.0

    async def test_list_by_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        rows = await repo.list_by_month("2026-01")
        assert len(rows) > 0

    async def test_aggregate_by_dept_month(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository

        repo = ShouldBeCapacityRepository(session)
        rows = await repo.aggregate_by_dept_month(["2026-01", "2026-02"], 2)
        assert len(rows) > 0


class TestProjectCategoryRepositoryExtended:
    async def test_get_by_name(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        cat = await repo.get_by_name("快服务")
        assert cat is not None
        assert cat.category_level == 2

    async def test_get_by_name_missing(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        cat = await repo.get_by_name("不存在的分类")
        assert cat is None

    async def test_get_level3(self, session: AsyncSession) -> None:
        await _seed_categories(session)
        from app.repositories.project_category_repository import ProjectCategoryRepository

        repo = ProjectCategoryRepository(session)
        cats = await repo.get_by_level3()
        assert len(cats) == 3
        for c in cats:
            assert c.category_level == 3


# ==============================================================================
# 补充 Service 层边界测试
# ==============================================================================


class TestCapacityAuditServiceExtended:
    async def test_summary_with_dept_filter(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_summary(time_period="2026-H1", dept_level=2, dept_name="基础平台组")
        assert float(str(result["should_be_days"])) >= 0

    async def test_summary_with_role_filter(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_summary(time_period="2026-H1", role="后端开发")
        assert float(str(result["should_be_days"])) >= 0

    async def test_zero_filling_with_dept(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_zero_filling(dept_level=2, dept_name="产品组")
        assert isinstance(result, list)

    async def test_deviation_ranking_positive_only(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_deviation_ranking(deviation_direction="positive")
        for r in result:
            assert float(str(r["deviation"])) > 0

    async def test_deviation_ranking_abnormal_only(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        await _seed_should_be_capacity(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_deviation_ranking(is_abnormal_only=True)
        for r in result:
            assert r["is_abnormal"] is True

    async def test_person_monthly_missing(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.capacity_audit_service import CapacityAuditService

        svc = CapacityAuditService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ShouldBeCapacityRepository(session),
        )
        result = await svc.get_person_monthly(9999)
        assert result["employee_id"] == 9999
        assert result["name"] == ""


class TestCrossAnalysisServiceExtended:
    async def test_get_role_monthly_trend_no_role(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_role_monthly_trend()
        assert result == []

    async def test_get_matrix_role_dimension(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
        from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.cross_analysis_service import CrossAnalysisService

        svc = CrossAnalysisService(
            EmployeeRepository(session),
            WorkHourRepository(session),
            ProjectCategoryRepository(session),
            ShouldBeCapacityRepository(session),
            ThreeFastPlanRepository(session),
        )
        result = await svc.get_matrix(row_dimension="role")
        assert "depts" in result
        assert "matrix" in result


class TestDrillDownServiceExtended:
    async def test_get_category_projects_no_category(self, session: AsyncSession) -> None:
        await _seed_employees(session)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_category_projects()
        assert result == []

    async def test_get_category_projects_with_dept(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_category_projects(
            time_period="2026-H1", category_id=7, dept_level=2, dept_name="基础平台组"
        )
        assert len(result) > 0

    async def test_get_category_projects_with_role(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_categories(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_category_projects(time_period="2026-H1", category_id=7, role="后端开发")
        assert len(result) > 0

    async def test_get_dept_children_no_parent(self, session: AsyncSession) -> None:
        emps = await _seed_employees(session)
        await _seed_work_hours(session, emps)
        from app.repositories.employee_repository import EmployeeRepository
        from app.repositories.project_category_repository import ProjectCategoryRepository
        from app.repositories.work_hour_repository import WorkHourRepository
        from app.services.drill_down_service import DrillDownService

        svc = DrillDownService(
            WorkHourRepository(session),
            EmployeeRepository(session),
            ProjectCategoryRepository(session),
        )
        result = await svc.get_dept_children(dept_level=2)
        assert len(result) > 0
