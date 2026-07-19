"""应有产能计算引擎单元测试: 工作日计算 + 在职折算(纯计算, 无 I/O)。"""

from datetime import date

from app.services.should_be_capacity_engine import (
    _count_workdays,
    calculate_all,
    calculate_monthly,
    get_h1_months,
)


class TestCountWorkdays:
    def test_should_count_weekdays_only(self) -> None:
        # 2026-06-01 周一 -> 2026-06-05 周五 = 5 个工作日
        count = _count_workdays(date(2026, 6, 1), date(2026, 6, 5), set(), set())
        assert count == 5

    def test_should_exclude_weekends(self) -> None:
        # 2026-06-01 周一 -> 2026-06-07 周日 = 5 个工作日+ 2 个周末
        count = _count_workdays(date(2026, 6, 1), date(2026, 6, 7), set(), set())
        assert count == 5

    def test_should_subtract_holidays(self) -> None:
        # 2026-06-01 周一 -> 2026-06-03 周三, 中间 6/2 是假日
        holidays = {date(2026, 6, 2)}
        count = _count_workdays(date(2026, 6, 1), date(2026, 6, 3), holidays, set())
        assert count == 2

    def test_should_add_makeup_weekend(self) -> None:
        # 2026-07-11 周六 -> 2026-07-12 周日, 其中 7/11 补班
        makeups = {date(2026, 7, 11)}  # 周六
        count = _count_workdays(date(2026, 7, 11), date(2026, 7, 12), set(), makeups)
        assert count == 1


class TestCalculateMonthly:
    def _make_emp(
        self,
        eid: int = 1,
        entry: date | None = None,
        leave: date | None = None,
        status: str = "在职",
        is_excluded: bool = False,
    ) -> dict[str, object]:
        return {
            "id": eid,
            "entry_date": entry,
            "leave_date": leave,
            "employee_status": status,
            "is_excluded": is_excluded,
        }

    def test_should_calculate_full_month_2026_01(self) -> None:
        # 2026-01: 22 工作日(无假日无补班)
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-01", set(), set())
        assert record["total_working_days"] == 22
        assert record["active_working_days"] == 22
        assert record["capacity_days"] == 22.0

    def test_should_calculate_full_month_2026_02(self) -> None:
        # 2026-02: 16 工作日(扣除春节 5 天(周一~周五 2/16~2/20) + 补班 1 天(2/14 周六))
        holidays = {
            date(2026, 2, 16),
            date(2026, 2, 17),
            date(2026, 2, 18),
            date(2026, 2, 19),
            date(2026, 2, 20),
        }
        makeups = {date(2026, 2, 14)}  # 周六补班
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-02", holidays, makeups)
        assert record["total_working_days"] == 16
        assert record["capacity_days"] == 16.0

    def test_should_calculate_full_month_2026_03(self) -> None:
        # 2026-03: 23 工作日(补班 3/1 周日)
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-03", set(), {date(2026, 3, 1)})
        assert record["total_working_days"] == 23
        assert record["capacity_days"] == 23.0

    def test_should_calculate_full_month_2026_04(self) -> None:
        # 2026-04: 21 工作日(清明 4/5 周日, 补休 4/6 周一)
        holidays = {date(2026, 4, 6)}
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-04", holidays, set())
        assert record["total_working_days"] == 21
        assert record["capacity_days"] == 21.0

    def test_should_calculate_full_month_2026_05(self) -> None:
        # 2026-05: 19 工作日(五一 5/1,5/4,5/5 共 3 个工作日放假, 5/9 补班)
        # 5/1 Fri, 5/4 Mon, 5/5 Tue = 3 weekdays
        holidays = {date(2026, 5, 1), date(2026, 5, 4), date(2026, 5, 5)}
        makeups = {date(2026, 5, 9)}
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-05", holidays, makeups)
        assert record["total_working_days"] == 19
        assert record["capacity_days"] == 19.0

    def test_should_calculate_full_month_2026_06(self) -> None:
        # 2026-06: 21 工作日(端午)
        holidays = {date(2026, 6, 19)}
        emp = self._make_emp()
        record = calculate_monthly(emp, "2026-06", holidays, set())
        assert record["total_working_days"] == 21
        assert record["capacity_days"] == 21.0

    def test_should_return_zero_for_left_before_month(self) -> None:
        emp = self._make_emp(leave=date(2025, 12, 31), status="离职")
        record = calculate_monthly(emp, "2026-01", set(), set())
        assert record["capacity_days"] == 0.0
        assert record["active_working_days"] == 0

    def test_should_return_zero_for_pending_entry_after_month(self) -> None:
        emp = self._make_emp(entry=date(2026, 7, 1), status="待入职")
        record = calculate_monthly(emp, "2026-01", set(), set())
        assert record["capacity_days"] == 0.0
        assert record["active_working_days"] == 0

    def test_should_return_zero_for_excluded_employee(self) -> None:
        emp = self._make_emp(is_excluded=True)
        record = calculate_monthly(emp, "2026-01", set(), set())
        assert record["capacity_days"] == 0.0

    def test_should_prorate_for_mid_month_entry(self) -> None:
        # 入职日 2026-01-05(周一), 1-2 号不是工作日, 当月 22 工作日
        # 从 1/5 开始的工作日 = 当月剩余工作日
        emp = self._make_emp(entry=date(2026, 1, 5))
        record = calculate_monthly(emp, "2026-01", set(), set())
        # 1/1 周四, 1/2 周五(2工作日), 1/5 开始剩余 20 工作日
        assert record["active_working_days"] == 20
        assert record["capacity_days"] == 20.0
        assert record["total_working_days"] == 22

    def test_should_prorate_for_mid_month_leave(self) -> None:
        emp = self._make_emp(leave=date(2026, 1, 5))
        record = calculate_monthly(emp, "2026-01", set(), set())
        # 1/1 周四+1/2 周五+1/5 周一 = 3 个工作日
        assert record["active_working_days"] == 3
        assert record["capacity_days"] == 3.0


class TestCalculateAll:
    def test_should_exclude_excluded_employees(self) -> None:
        emp1: dict[str, object] = {
            "id": 1,
            "is_excluded": True,
            "entry_date": None,
            "leave_date": None,
            "employee_status": "在职",
        }
        emp2: dict[str, object] = {
            "id": 2,
            "is_excluded": False,
            "entry_date": None,
            "leave_date": None,
            "employee_status": "在职",
        }
        employees = [emp1, emp2]
        months = ["2026-01"]
        records = calculate_all(employees, months, set(), set())
        assert len(records) == 1
        assert records[0]["employee_id"] == 2

    def test_should_only_return_records_with_capacity(self) -> None:
        emp: dict[str, object] = {
            "id": 1,
            "is_excluded": False,
            "entry_date": date(2026, 7, 1),
            "leave_date": None,
            "employee_status": "待入职",
        }
        records = calculate_all([emp], ["2026-01"], set(), set())
        assert len(records) == 0


class TestGetH1Months:
    def test_should_return_6_months(self) -> None:
        months = get_h1_months()
        assert len(months) == 6
        assert months[0] == "2026-01"
        assert months[-1] == "2026-06"
