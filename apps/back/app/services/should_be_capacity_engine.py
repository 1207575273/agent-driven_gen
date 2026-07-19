"""应有产能计算引擎: 工作日计算 + 在职折算。

预计算在导入时触发, 结果存储到 should_be_capacity 表。
"""

import calendar
from datetime import date, timedelta

# 月数常量
_MONTHS_IN_H1 = list(range(1, 7))


def calculate_monthly(
    employee: dict[str, object],
    year_month: str,
    holiday_dates_set: set[date],
    makeup_dates_set: set[date],
) -> dict[str, object]:
    """计算单人在单月的应有产能。

    Args:
        employee: 员工 dict(含 id/entry_date/leave_date/employee_status/is_excluded)
        year_month: 月份 "2026-01"
        holiday_dates_set: 假日日期集合(非工作日)
        makeup_dates_set: 补班日期集合(工作日)

    Returns:
        dict: {employee_id, year_month, total_working_days, active_working_days, capacity_days}
    """
    year = int(year_month[:4])
    month = int(year_month[5:7])
    month_start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    month_end = date(year, month, last_day)

    # 1. 计算当月总工作日
    total_working_days = _count_workdays(month_start, month_end, holiday_dates_set, makeup_dates_set)

    # 2. 判断是否整月在职
    entry_val = employee.get("entry_date")
    leave_val = employee.get("leave_date")
    status = str(employee.get("employee_status", ""))

    entry_date: date | None = entry_val if isinstance(entry_val, date) else None
    leave_date: date | None = leave_val if isinstance(leave_val, date) else None

    # 已离职且离职日期在月初之前 -> 不计
    if status == "离职" and leave_date is not None and leave_date < month_start:
        return {
            "employee_id": employee["id"],
            "year_month": year_month,
            "total_working_days": total_working_days,
            "active_working_days": 0,
            "capacity_days": 0.0,
        }

    # 待入职且入职日期在月末之后 -> 不计
    if status == "待入职" and entry_date is not None and entry_date > month_end:
        return {
            "employee_id": employee["id"],
            "year_month": year_month,
            "total_working_days": total_working_days,
            "active_working_days": 0,
            "capacity_days": 0.0,
        }

    # 排除勉填/异常未填人员: 应有产能记为 0
    if employee.get("is_excluded") or employee.get("is_excluded_bool"):
        return {
            "employee_id": employee["id"],
            "year_month": year_month,
            "total_working_days": total_working_days,
            "active_working_days": 0,
            "capacity_days": 0.0,
        }

    # 3. 计算在职工作日
    effective_start = max(month_start, entry_date) if entry_date else month_start
    effective_end = min(month_end, leave_date) if leave_date else month_end

    active_working_days = _count_workdays(effective_start, effective_end, holiday_dates_set, makeup_dates_set)

    return {
        "employee_id": employee["id"],
        "year_month": year_month,
        "total_working_days": total_working_days,
        "active_working_days": active_working_days,
        "capacity_days": float(active_working_days),
    }


def calculate_all(
    employees: list[dict[str, object]],
    year_months: list[str],
    holiday_dates_set: set[date],
    makeup_dates_set: set[date],
) -> list[dict[str, object]]:
    """批量计算所有排除人员的应有产能。

    Args:
        employees: 员工列表
        year_months: 月份列表 ["2026-01", "2026-02", ...]
        holiday_dates_set: 假日日期集合
        makeup_dates_set: 补班日期集合

    Returns:
        应有产能记录列表
    """
    results: list[dict[str, object]] = []
    for emp in employees:
        # 排除勉填/异常未填人员
        if emp.get("is_excluded") or emp.get("is_excluded_bool"):
            continue
        for ym in year_months:
            record = calculate_monthly(emp, ym, holiday_dates_set, makeup_dates_set)
            # 只保留 capacity_days > 0 的记录
            if float(record["capacity_days"]) > 0:  # type: ignore[arg-type]
                results.append(record)
    return results


def _count_workdays(start: date, end: date, holidays: set[date], makeups: set[date]) -> int:
    """计算日期区间内的工作日数(周一至周五 - 假日 + 补班)。"""
    count = 0
    current = start
    while current <= end:
        is_weekday = current.weekday() < 5
        is_holiday = current in holidays
        is_makeup = current in makeups
        if (is_weekday and not is_holiday) or is_makeup:
            count += 1
        current += timedelta(days=1)
    return count


def get_h1_months() -> list[str]:
    """返回 2026-H1 的月份列表。"""
    return ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]


def get_months_for_h1() -> list[str]:
    """返回 2026-H1 的月份列表(别名)。"""
    return get_h1_months()
