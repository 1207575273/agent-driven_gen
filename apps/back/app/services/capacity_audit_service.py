"""产能填报审计服务: 应有 vs 实际对比、填报率、偏差判定、异常标记。"""

from datetime import date
from typing import Any

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
from app.repositories.work_hour_repository import WorkHourRepository

# 偏差异常判定阈值
DEVIATION_ABS_THRESHOLD = 3.0  # |偏差| > 3 人天
DEVIATION_RATE_THRESHOLD = 30.0  # 偏差率 > 30%


def _is_abnormal(deviation: float, should_be_days: float) -> bool:
    """判断是否偏差异常: |偏差| > 3 人天 且 偏差率 > 30%。"""
    if should_be_days <= 0:
        return False
    deviation_rate = abs(deviation) / should_be_days * 100
    return abs(deviation) > DEVIATION_ABS_THRESHOLD and deviation_rate > DEVIATION_RATE_THRESHOLD


def _parse_year_months(time_period: str | None) -> list[str]:
    """解析时间范围参数为月份列表。

    Args:
        time_period: "2026-H1" / "2026-Q1" / "2026-Q2" / "2026-01" 等

    Returns:
        月份列表如 ["2026-01", "2026-02"]
    """
    if not time_period:
        return ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]

    tp = time_period.strip()
    if tp == "2026-H1":
        return ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    elif tp == "2026-Q1":
        return ["2026-01", "2026-02", "2026-03"]
    elif tp == "2026-Q2":
        return ["2026-04", "2026-05", "2026-06"]
    elif "-" in tp and len(tp) == 7:
        return [tp]
    return [tp]


def _year_month_to_date_range(year_months: list[str]) -> tuple[date, date]:
    """将月份列表转为起止日期范围。"""
    import calendar

    start_month = year_months[0]
    end_month = year_months[-1]
    start = date(int(start_month[:4]), int(start_month[5:7]), 1)
    y, m = int(end_month[:4]), int(end_month[5:7])
    last_day = calendar.monthrange(y, m)[1]
    end = date(y, m, last_day)
    return start, end


class CapacityAuditService:
    """产能填报审计服务: KPI 汇总、月度趋势、填报率、零填报、偏差排行、异常明细。"""

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        work_hour_repo: WorkHourRepository,
        capacity_repo: ShouldBeCapacityRepository,
    ) -> None:
        self._emp_repo = employee_repo
        self._wh_repo = work_hour_repo
        self._cap_repo = capacity_repo

    async def get_summary(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> dict[str, object]:
        """审计汇总 KPI: 应有产能、实际产能、填报率、偏差、人员数、零填报、异常数。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        # 筛选员工
        emp_ids = await self._resolve_employee_ids(dept_level, dept_name, role)

        # 应有产能汇总
        should_be = await self._cap_repo.get_total_by_period(year_months, emp_ids)
        should_be_days = float(str(should_be.get("should_be_days", 0.0)))

        # 实际产能汇总: 直接用 repo 聚合人员工时
        actual_data = await self._wh_repo.aggregate_by_person_and_category(start_date, end_date, emp_ids)
        actual_days = sum(float(str(r.get("actual_days", 0))) for r in actual_data)

        # 填报率
        fill_rate = round(actual_days / should_be_days * 100, 2) if should_be_days > 0 else 0.0

        # 偏差
        deviation = round(actual_days - should_be_days, 1)

        # 人数
        employee_count = int(float(str(should_be.get("person_count", 0))))

        # 零填报: actual_days=0 且应有产能>0 的人员
        zero_fill_count = await self._count_zero_fill(start_date, end_date, emp_ids, year_months)

        # 异常人数
        abnormal_count = await self._count_abnormal(start_date, end_date, emp_ids, year_months)

        return {
            "should_be_days": round(should_be_days, 1),
            "actual_days": round(actual_days, 1),
            "fill_rate": fill_rate,
            "deviation": deviation,
            "employee_count": employee_count,
            "zero_fill_count": zero_fill_count,
            "abnormal_count": abnormal_count,
        }

    async def get_monthly_trend(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, object]]:
        """月度应有 vs 实际趋势。"""
        year_months = _parse_year_months(time_period)
        emp_ids = await self._resolve_employee_ids(dept_level, dept_name, role)

        # 应有产能按月汇总
        sbc_monthly = await self._cap_repo.aggregate_by_month(year_months, emp_ids)

        # 实际产能按月汇总
        start_date, end_date = _year_month_to_date_range(year_months)
        wh_monthly = await self._wh_repo.aggregate_by_time_and_category(
            start_date, end_date, 1, employee_ids=emp_ids
        )

        # 合并
        wh_map: dict[str, float] = {}
        for r in wh_monthly:
            month = str(r.get("month", ""))
            days = float(str(r.get("person_days", 0)))
            wh_map[month] = wh_map.get(month, 0.0) + days

        result: list[dict[str, object]] = []
        for sbc in sbc_monthly:
            month = str(sbc.get("year_month", ""))
            should_be = float(str(sbc.get("should_be_days", 0)))
            actual = wh_map.get(month, 0.0)
            fr = round(actual / should_be * 100, 2) if should_be > 0 else 0.0
            result.append(
                {
                    "month": month,
                    "should_be_days": round(should_be, 1),
                    "actual_days": round(actual, 1),
                    "fill_rate": fr,
                    "deviation": round(actual - should_be, 1),
                    "working_days": int(float(str(sbc.get("total_working_days", 0)))),
                }
            )
        return result

    async def get_department_fill_rate(
        self,
        time_period: str | None = None,
        dept_level: int = 2,
        parent_dept: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, object]]:
        """部门填报率排行。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        # 筛选员工(如果指定了上级部门, 按上级部门+下一层级筛选)
        emp_ids = await self._resolve_employee_ids(dept_level, parent_dept, role)

        # 应有产能按部门汇总
        sbc_dept = await self._cap_repo.aggregate_by_dept_month(year_months, dept_level, emp_ids)

        # 实际产能按部门汇总
        wh_dept = await self._wh_repo.aggregate_by_dept_and_category(start_date, end_date, dept_level, 1, emp_ids)

        # 合并
        sbc_map: dict[str, float] = {}
        person_map: dict[str, int] = {}
        for r in sbc_dept:
            dept = str(r.get("dept_name", ""))
            if dept and dept != "None":
                sbc_map[dept] = sbc_map.get(dept, 0.0) + float(str(r.get("should_be_days", 0)))
                # 取该部门所有月份 person_count 的最大值(每个月的 distinct count)
                pc = int(float(str(r.get("person_count", 0))))
                person_map[dept] = max(person_map.get(dept, 0), pc)
        wh_map: dict[str, float] = {}
        for r in wh_dept:
            dept = str(r.get("dept_name", ""))
            if dept and dept != "None":
                wh_map[dept] = wh_map.get(dept, 0.0) + float(str(r.get("person_days", 0)))

        # 获取所有部门名，排除空值和 None
        all_dept_names = {d for d in (set(sbc_map.keys()) | set(wh_map.keys())) if d and d != "None"}

        result: list[dict[str, object]] = []
        for dept_name in sorted(all_dept_names):
            should_be = sbc_map.get(dept_name, 0.0)
            actual = wh_map.get(dept_name, 0.0)
            fr = round(actual / should_be * 100, 2) if should_be > 0 else 0.0
            # 检查是否有子节点
            has_children = dept_level < 4

            # 统计该部门下异常人数（所有层级）
            dept_abnormal = await self._count_abnormal_in_dept(
                start_date, end_date, dept_name, dept_level, year_months
            )

            result.append(
                {
                    "dept_name": dept_name,
                    "dept_path": parent_dept + "/" + dept_name if parent_dept else dept_name,
                    "dept_level": dept_level,
                    "should_be_days": round(should_be, 1),
                    "actual_days": round(actual, 1),
                    "fill_rate": fr,
                    "deviation": round(actual - should_be, 1),
                    "abnormal_count": dept_abnormal,
                    "person_count": person_map.get(dept_name, 0),
                    "has_children": has_children,
                }
            )
        # 按填报率排序
        result.sort(key=lambda x: float(str(x["fill_rate"])), reverse=True)  # type: ignore[arg-type]
        return result

    async def get_zero_filling(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
    ) -> list[dict[str, object]]:
        """零填报人员列表(排除了勉填/异常未填/已离职/待入职未到日期)。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        # 获取正常在职人员
        employees = await self._emp_repo.list_active_normal()
        if dept_level and dept_name:
            dept_employees = await self._emp_repo.list_by_department(dept_level, dept_name)
            dept_ids = {e.id for e in dept_employees}
            employees = [e for e in employees if e.id in dept_ids]

        result: list[dict[str, object]] = []
        for emp in employees:
            # 应有产能
            sbc_total = 0.0
            for ym in year_months:
                sbc = await self._cap_repo.get_by_employee_month(emp.id, ym)  # type: ignore[arg-type]
                if sbc:
                    sbc_total += float(sbc.capacity_days)

            # 实际产能
            actual_data = await self._wh_repo.aggregate_by_person_and_category(
                start_date,
                end_date,
                [emp.id] if emp.id is not None else None,  # type: ignore[arg-type]
            )
            actual_days = sum(float(str(r.get("actual_days", 0))) for r in actual_data)
            if sbc_total > 0 and actual_days == 0:
                result.append(
                    {
                        "employee_id": emp.id,
                        "name": emp.name,
                        "employee_id_str": emp.employee_id or "",
                        "dept_name": emp.level2_dept or "",
                        "dept_path": _build_dept_path(emp),
                        "role": emp.role or "",
                        "should_be_days": round(sbc_total, 1),
                        "actual_days": 0.0,
                        "entry_date": emp.entry_date.isoformat() if emp.entry_date else None,
                        "fill_note": emp.fill_note or "",
                    }
                )
        return result

    async def get_deviation_ranking(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
        deviation_direction: str = "all",
        sort_by: str = "deviation_abs",
        sort_dir: str = "desc",
        is_abnormal_only: bool = False,
    ) -> list[dict[str, object]]:
        """偏差异常排行。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)
        emp_ids = await self._resolve_employee_ids(dept_level, dept_name, role)

        actual_rows = await self._wh_repo.aggregate_by_person_and_category(start_date, end_date, emp_ids)
        actual_map: dict[int, dict[str, object]] = {}
        for r in actual_rows:
            eid = int(float(str(r.get("employee_id", 0))))
            actual_map[eid] = r

        # 应有产能按人汇总
        sbc_map: dict[int, float] = {}
        for ym in year_months:
            sbc_list = await self._cap_repo.list_by_month(ym)
            for sbc in sbc_list:
                if emp_ids and sbc.employee_id not in emp_ids:
                    continue
                sbc_map[sbc.employee_id] = sbc_map.get(sbc.employee_id, 0.0) + float(sbc.capacity_days)

        result: list[dict[str, object]] = []
        all_eids = set(actual_map.keys()) | set(sbc_map.keys())

        # 预加载所有有应有产能但无实际工时的人员信息
        fallback_ids = [eid for eid in sbc_map if eid not in actual_map]
        employee_fallback: dict[int, Any] = {}
        if fallback_ids:
            from sqlmodel import select as sm_select

            from app.models.employee import Employee as EmpModel
            emp_result = await self._wh_repo._session.exec(sm_select(EmpModel).where(EmpModel.id.in_(fallback_ids)))  # type: ignore[arg-type,union-attr]
            for emp in emp_result.all():
                if emp.id is not None:
                    employee_fallback[emp.id] = emp  # type: ignore[union-attr,index]

        for eid in all_eids:
            should_be = sbc_map.get(eid, 0.0)
            actual = float(str(actual_map.get(eid, {}).get("actual_days", 0.0)))
            deviation = actual - should_be
            deviation_rate = abs(deviation) / should_be * 100 if should_be > 0 else 0.0
            abnormal = _is_abnormal(deviation, should_be)

            if is_abnormal_only and not abnormal:
                continue

            # 偏差方向过滤
            if deviation_direction == "positive" and deviation <= 0:
                continue
            if deviation_direction == "negative" and deviation >= 0:
                continue

            row_data: dict[str, object] = actual_map.get(eid, {})
            if not row_data and eid in employee_fallback:
                fb_emp = employee_fallback[eid]
                row_data = {
                    "name": fb_emp.name or "",  # type: ignore[union-attr]
                    "employee_id_str": fb_emp.employee_id or "",  # type: ignore[union-attr]
                    "dept_name": fb_emp.level2_dept or "",  # type: ignore[union-attr]
                    "dept_path": fb_emp.level2_dept or "",  # type: ignore[union-attr]
                    "role": fb_emp.role or "",  # type: ignore[union-attr]
                }
            result.append(
                {
                    "employee_id": eid,
                    "name": row_data.get("name", ""),
                    "employee_id_str": row_data.get("employee_id_str", ""),
                    "dept_name": row_data.get("dept_name", ""),
                    "dept_path": row_data.get("dept_path", row_data.get("dept_name", "")),
                    "role": row_data.get("role", ""),
                    "should_be_days": round(should_be, 1),
                    "actual_days": round(actual, 1),
                    "deviation": round(deviation, 1),
                    "deviation_rate": round(deviation_rate, 1),
                    "deviation_abs": round(abs(deviation), 1),
                    "is_abnormal": abnormal,
                    "project_count": int(float(str(row_data.get("project_count", 0)))),
                }
            )

        # 排序
        reverse = sort_dir == "desc"
        sort_keys: dict[str, object] = {
            "deviation_abs": lambda x: float(str(x.get("deviation_abs", 0))),
            "deviation_rate": lambda x: float(str(x.get("deviation_rate", 0))),
            "should_be_days": lambda x: float(str(x.get("should_be_days", 0))),
            "actual_days": lambda x: float(str(x.get("actual_days", 0))),
            "deviation": lambda x: float(str(x.get("deviation", 0))),
        }
        key_fn = sort_keys.get(sort_by, sort_keys["deviation_abs"])
        result.sort(key=key_fn, reverse=reverse)  # type: ignore[arg-type]
        return result

    async def get_abnormal_detail(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
    ) -> list[dict[str, object]]:
        """异常人员明细。"""
        return await self.get_deviation_ranking(
            time_period=time_period,
            dept_level=dept_level,
            dept_name=dept_name,
            role=None,
            deviation_direction="all",
            sort_by="deviation_abs",
            sort_dir="desc",
            is_abnormal_only=True,
        )

    async def get_person_monthly(
        self,
        employee_id: int,
    ) -> dict[str, object]:
        """人员月度明细(下钻用)。"""
        emp = await self._emp_repo.get(employee_id)
        if emp is None:
            return {"employee_id": employee_id, "name": "", "monthly_data": []}

        year_months = _parse_year_months("2026-H1")
        start_date, end_date = _year_month_to_date_range(year_months)

        # 应有产能按月
        sbc_data = await self._cap_repo.list_by_employee(employee_id)
        sbc_map: dict[str, float] = {}
        for sbc in sbc_data:
            sbc_map[sbc.year_month] = float(sbc.capacity_days)

        # 实际产能按月
        wh_data = await self._wh_repo.aggregate_by_person_month(employee_id, start_date, end_date)
        wh_map: dict[str, float] = {}
        for r in wh_data:
            wh_map[str(r.get("month", ""))] = float(str(r.get("actual_days", 0)))

        monthly_data: list[dict[str, object]] = []
        for ym in year_months:
            should_be = sbc_map.get(ym, 0.0)
            actual = wh_map.get(ym, 0.0)
            deviation = actual - should_be
            fill_rate = round(actual / should_be * 100, 2) if should_be > 0 else 0.0
            monthly_data.append(
                {
                    "month": ym,
                    "should_be_days": round(should_be, 1),
                    "actual_days": round(actual, 1),
                    "deviation": round(deviation, 1),
                    "fill_rate": fill_rate,
                }
            )

        return {
            "employee_id": employee_id,
            "name": emp.name,
            "monthly_data": monthly_data,
        }

    async def get_person_projects(
        self,
        employee_id: int,
        time_period: str | None = None,
    ) -> list[dict[str, object]]:
        """人员项目投入明细。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        projects = await self._wh_repo.get_person_projects(employee_id, start_date, end_date)

        result: list[dict[str, object]] = []
        for p in projects:
            proj_name = str(p.get("project_name", "") or "未分类")
            cat_name = str(p.get("category_name", "") or "未分类")
            cat_id = p.get("category_id")
            person_days = float(str(p.get("person_days", 0)))

            # 月度分布: 简单起见, 这里用汇总值, 后续 refine
            monthly_breakdown: list[dict[str, object]] = []

            result.append(
                {
                    "project_name": proj_name,
                    "category_path": cat_name,
                    "category_id": cat_id,
                    "person_days": round(person_days, 1),
                    "monthly_breakdown": monthly_breakdown,
                }
            )
        return result

    async def _resolve_employee_ids(
        self,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> list[int] | None:
        """将筛选条件转为员工 ID 列表。返回 None 表示不过滤。"""
        if not dept_name and not role:
            return None

        employees = await self._emp_repo.list_active_normal()
        result_ids: list[int] = []

        for emp in employees:
            match = True
            if dept_name and dept_level:
                col_name_map = {1: emp.level1_dept, 2: emp.level2_dept, 3: emp.level3_dept, 4: emp.level4_dept}
                if col_name_map.get(dept_level) != dept_name:
                    match = False
            if role and emp.role != role:
                match = False
            if match:
                result_ids.append(emp.id)  # type: ignore[arg-type]

        return result_ids if result_ids else None

    async def _count_zero_fill(
        self,
        start_date: date,
        end_date: date,
        emp_ids: list[int] | None,
        year_months: list[str],
    ) -> int:
        """统计零填报人数。"""
        employees = await self._emp_repo.list_active_normal()
        if emp_ids:
            employees = [e for e in employees if e.id in emp_ids]

        count = 0
        for emp in employees:
            sbc_total = 0.0
            for ym in year_months:
                sbc = await self._cap_repo.get_by_employee_month(emp.id, ym)  # type: ignore[arg-type]
                if sbc:
                    sbc_total += float(sbc.capacity_days)

            actual_data = await self._wh_repo.aggregate_by_person_and_category(
                start_date,
                end_date,
                [emp.id] if emp.id is not None else None,  # type: ignore[arg-type,list-item]
            )
            actual_days = sum(float(str(r.get("actual_days", 0))) for r in actual_data)

            if sbc_total > 0 and actual_days == 0:
                count += 1
        return count

    async def _count_abnormal(
        self,
        start_date: date,
        end_date: date,
        emp_ids: list[int] | None,
        year_months: list[str],
    ) -> int:
        """统计异常人数。"""
        ranking = await self.get_deviation_ranking(
            time_period=None,
            dept_level=None,
            dept_name=None,
            role=None,
            deviation_direction="all",
            is_abnormal_only=True,
        )
        # 如果 emp_ids 不为 None, 只统计其中的人员
        if emp_ids:
            ranking = [r for r in ranking if int(float(str(r.get("employee_id", 0)))) in emp_ids]
        return len(ranking)

    async def _count_abnormal_in_dept(
        self,
        start_date: date,
        end_date: date,
        dept_name: str,
        dept_level: int,
        year_months: list[str],
    ) -> int:
        """统计某部门下的异常人数(直接用 dept_name 过滤异常列表)。"""
        ranking = await self.get_deviation_ranking(
            time_period=None,
            dept_level=dept_level,
            dept_name=dept_name,
            role=None,
            deviation_direction="all",
            is_abnormal_only=True,
        )
        return len(ranking)


def _build_dept_path(emp: object) -> str:
    """构建部门路径。"""
    parts = []
    for attr in ["level1_dept", "level2_dept", "level3_dept", "level4_dept"]:
        val = getattr(emp, attr, None)
        if val:
            parts.append(str(val))
    return "/".join(parts)
