"""产能交叉维度分析服务: 时间x分类、部门x分类、角色x分类、人员排名、三快计划对比。"""

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.project_category_repository import ProjectCategoryRepository
from app.repositories.should_be_capacity_repository import ShouldBeCapacityRepository
from app.repositories.three_fast_plan_repository import ThreeFastPlanRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.capacity_audit_service import _parse_year_months, _year_month_to_date_range


class CrossAnalysisService:
    """产能交叉维度分析服务: 多维度交叉聚合、分类汇总、三快计划对比。"""

    def __init__(
        self,
        employee_repo: EmployeeRepository,
        work_hour_repo: WorkHourRepository,
        category_repo: ProjectCategoryRepository,
        capacity_repo: ShouldBeCapacityRepository,
        plan_repo: ThreeFastPlanRepository,
    ) -> None:
        self._emp_repo = employee_repo
        self._wh_repo = work_hour_repo
        self._cat_repo = category_repo
        self._cap_repo = capacity_repo
        self._plan_repo = plan_repo

    async def get_time_category(
        self,
        time_granularity: str = "month",
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
        category_level: int = 1,
        parent_category_id: int | None = None,
    ) -> list[dict[str, object]]:
        """时间 x 分类交叉分析。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, dept_name, role)  # type: ignore[attr-defined]

        # 按时间聚合
        wh_monthly = await self._wh_repo.aggregate_by_time_and_category(
            start_date, end_date, category_level, parent_category_id, emp_ids
        )

        # 构建 {时间标签: {分类名: (人天, category_id)}}
        time_cat: dict[str, dict[str, tuple[float, int]]] = {}
        for r in wh_monthly:
            month = str(r.get("month", ""))
            cat = str(r.get("category_name", ""))
            days = float(str(r.get("person_days", 0)))
            cat_id = int(float(str(r.get("category_id", 0))))
            if time_granularity == "quarter":
                label = _month_to_quarter(month)
            elif time_granularity == "half":
                label = "2026-H1"
            else:
                label = month
            if label not in time_cat:
                time_cat[label] = {}
            entry_cat = time_cat[label].get(cat, (0.0, 0))
            time_cat[label][cat] = (entry_cat[0] + days, cat_id if cat_id > 0 else entry_cat[1])  # type: ignore[arg-type]

        result: list[dict[str, object]] = []
        for label in sorted(time_cat.keys()):
            cats = time_cat[label]
            total_cat = sum(v[0] for v in cats.values())  # type: ignore[misc]
            entry: dict[str, object] = {"time_label": label, "person_days": total_cat}
            cats_list: list[dict[str, object]] = [
                {
                    "category_name": k,
                    "category_id": v[1],
                    "total_days": round(v[0], 1),
                    "percentage": round(v[0] / total_cat * 100, 1) if total_cat > 0 else 0.0,
                }
                for k, v in sorted(cats.items(), key=lambda x: -x[1][0])  # type: ignore[arg-type,misc]
            ]
            entry["categories"] = cats_list
            result.append(entry)
        return result

    async def get_should_vs_actual(
        self,
        time_granularity: str = "month",
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
    ) -> list[dict[str, object]]:
        """应有 vs 实际产能(按时间)。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, dept_name, None)  # type: ignore[attr-defined]

        sbc_monthly = await self._cap_repo.aggregate_by_month(year_months, emp_ids)
        wh_monthly = await self._wh_repo.aggregate_by_time_and_category(start_date, end_date, 1, employee_ids=emp_ids)

        wh_map: dict[str, float] = {}
        for r in wh_monthly:
            month = str(r.get("month", ""))
            days = float(str(r.get("person_days", 0)))
            wh_map[month] = wh_map.get(month, 0.0) + days

        result: list[dict[str, object]] = []
        for sbc in sbc_monthly:
            month = str(sbc.get("month", ""))
            should_be = float(str(sbc.get("should_be_days", 0)))
            actual = wh_map.get(month, 0.0)
            fr = round(actual / should_be * 100, 2) if should_be > 0 else 0.0

            if time_granularity == "quarter":
                label = _month_to_quarter(month)
            elif time_granularity == "half":
                label = "2026-H1"
            else:
                label = month

            result.append(
                {
                    "time_label": label,
                    "should_be_days": round(should_be, 1),
                    "actual_days": round(actual, 1),
                    "fill_rate": fr,
                    "deviation": round(actual - should_be, 1),
                }
            )
        return result

    async def get_dept_category(
        self,
        time_period: str | None = None,
        dept_level: int = 2,
        parent_dept: str | None = None,
        category_level: int = 1,
    ) -> list[dict[str, object]]:
        """组织 x 项目分类交叉分析。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, parent_dept, None)  # type: ignore[attr-defined]

        wh_dept = await self._wh_repo.aggregate_by_dept_and_category(
            start_date, end_date, dept_level, category_level, emp_ids
        )

        # 按部门分组
        dept_groups: dict[str, dict[str, object]] = {}
        dept_cat_ids: dict[str, dict[str, int]] = {}
        for r in wh_dept:
            dept = str(r.get("dept_name", ""))
            if dept not in dept_groups:
                dept_groups[dept] = {
                    "dept_name": dept,
                    "dept_path": dept,
                    "total_days": 0.0,
                    "category_distribution": {},
                }
                dept_cat_ids[dept] = {}
            days = float(str(r.get("person_days", 0)))
            cat = str(r.get("category_name", ""))
            cat_id = int(float(str(r.get("category_id", 0))))
            dept_groups[dept]["total_days"] = dept_groups[dept]["total_days"] + days  # type: ignore[operator]
            dist = dept_groups[dept].get("category_distribution", {})
            if isinstance(dist, dict) and cat:
                dist[cat] = dist.get(cat, 0.0) + days  # type: ignore[index]
            dept_cat_ids[dept][cat] = cat_id
        # Attach category_ids to each dept
        for dept, cat_ids in dept_cat_ids.items():
            dept_groups[dept]["category_ids"] = cat_ids  # type: ignore[index]

        return sorted(dept_groups.values(), key=lambda x: float(str(x["total_days"])), reverse=True)  # type: ignore[arg-type]

    async def get_dept_category_matrix(
        self,
        time_period: str | None = None,
        dept_level: int = 2,
        category_level: int = 1,
    ) -> dict[str, object]:
        """部门分类偏好(热力图数据)。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        wh_dept = await self._wh_repo.aggregate_by_dept_and_category(start_date, end_date, dept_level, category_level)

        dept_set: set[str] = set()
        cat_set: set[str] = set()
        # matrix_data[dept][cat] = days
        matrix_data: dict[str, dict[str, float]] = {}

        for r in wh_dept:
            dept = str(r.get("dept_name", ""))
            cat = str(r.get("category_name", ""))
            days = float(str(r.get("person_days", 0)))
            dept_set.add(dept)
            cat_set.add(cat)
            if dept not in matrix_data:
                matrix_data[dept] = {}
            matrix_data[dept][cat] = matrix_data[dept].get(cat, 0.0) + days

        cat_names = sorted(cat_set)
        depts_sorted = sorted(dept_set)
        matrix: list[list[float]] = []
        for dept in depts_sorted:
            row = [matrix_data.get(dept, {}).get(cat, 0.0) for cat in cat_names]
            matrix.append(row)

        return {
            "depts": depts_sorted,
            "categories": cat_names,
            "matrix": matrix,
        }

    async def get_role_category(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        category_level: int = 1,
    ) -> list[dict[str, object]]:
        """角色 x 项目分类交叉分析。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, dept_name, None)  # type: ignore[attr-defined]

        wh_role = await self._wh_repo.aggregate_by_role_and_category(start_date, end_date, category_level, emp_ids)

        # 按角色名合并, 填入分类分布
        role_groups: dict[str, dict[str, object]] = {}
        role_cat_ids: dict[str, dict[str, int]] = {}
        for r in wh_role:
            role_name = str(r.get("role", ""))
            cat_name = str(r.get("category_name", ""))
            days = float(str(r.get("person_days", 0)))
            cnt = int(float(str(r.get("person_count", 0))))
            cat_id = int(float(str(r.get("category_id", 0))))
            if role_name not in role_groups:
                role_groups[role_name] = {
                    "role": role_name,
                    "person_count": 0,
                    "total_days": 0.0,
                    "avg_days_per_person": 0.0,
                    "category_distribution": {},
                }
                role_cat_ids[role_name] = {}
            grp = role_groups[role_name]
            grp["person_count"] = max(int(float(str(grp["person_count"]))), cnt)  # type: ignore[operator]
            role_cat_ids[role_name][cat_name] = cat_id
            grp["total_days"] = grp["total_days"] + days  # type: ignore[operator]
            dist = grp.get("category_distribution", {})
            if isinstance(dist, dict) and cat_name:
                dist[cat_name] = dist.get(cat_name, 0.0) + days  # type: ignore[index]
            # 人均在最后计算
        for role_name, grp in role_groups.items():
            pc = max(1, int(float(str(grp.get("person_count", 1)))))
            td = float(str(grp.get("total_days", 0)))
            grp["avg_days_per_person"] = round(td / pc, 1)
            grp["category_ids"] = role_cat_ids.get(role_name, {})  # type: ignore[index]

        return sorted(role_groups.values(), key=lambda x: float(str(x["total_days"])), reverse=True)  # type: ignore[arg-type]

    async def get_role_monthly_trend(
        self,
        time_period: str | None = None,
        role: str | None = None,
        category_level: int = 1,
    ) -> list[dict[str, object]]:
        """角色月度趋势。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        if not role:
            return []

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(None, None, role)  # type: ignore[attr-defined]

        wh_monthly = await self._wh_repo.aggregate_by_time_and_category(
            start_date, end_date, category_level, employee_ids=emp_ids
        )

        month_map: dict[str, dict[str, object]] = {}
        for r in wh_monthly:
            month = str(r.get("month", ""))
            days = float(str(r.get("person_days", 0)))
            cat = str(r.get("category_name", ""))
            if month not in month_map:
                month_map[month] = {"month": month, "category_distribution": {}, "total_days": 0.0}
            month_map[month]["total_days"] = month_map[month]["total_days"] + days  # type: ignore[operator]
            dist = month_map[month].get("category_distribution", {})
            if isinstance(dist, dict) and cat:
                dist[cat] = dist.get(cat, 0.0) + days  # type: ignore[index]

        return sorted(month_map.values(), key=lambda x: str(x["month"]))

    async def get_person_ranking(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
        sort_by: str = "actual_days",
        sort_dir: str = "desc",
    ) -> list[dict[str, object]]:
        """人员维度排名。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, dept_name, role)  # type: ignore[attr-defined]

        ranked = await self._wh_repo.rank_by_person(start_date, end_date, emp_ids, sort_by, sort_dir)

        # 附加应有产能
        for r in ranked:
            eid = int(float(str(r.get("employee_id", 0))))
            sbc_total = 0.0
            for ym in year_months:
                sbc = await self._cap_repo.get_by_employee_month(eid, ym)
                if sbc:
                    sbc_total += float(sbc.capacity_days)
            r["should_be_days"] = round(sbc_total, 1)
            actual = float(str(r.get("actual_days", 0)))
            r["deviation"] = round(actual - sbc_total, 1)

        return list(ranked)

    async def get_three_fast_comparison(
        self,
        time_period: str | None = None,
    ) -> list[dict[str, object]]:
        """三快计划 vs 实际对比。按月导入计划，按季度聚合返回。"""
        plans = await self._plan_repo.list_all()

        from sqlalchemy import func as sa_func
        from sqlmodel import select

        from app.models.work_hour import WorkHour

        # (quarter_label, cat_id) -> {plan, actual}
        Q_map: dict[str, dict[int, dict[str, object]]] = {"2026-Q1": {}, "2026-Q2": {}}
        for plan in plans:
            cat = await self._cat_repo.get(plan.category_id)
            cat_name = cat.category_name if cat else "未知分类"
            if cat_name not in ("快服务", "快交付", "快营销"):
                continue
            cid = plan.category_id

            # 该月实际产能
            ym = plan.plan_quarter
            if "Q" in ym:
                q_num = int(ym.split("Q")[1])
                m = (q_num - 1) * 3 + 1
                ms, me = _year_month_to_date_range([f"2026-{m:02d}"])
            else:
                ms, me = _year_month_to_date_range([ym])

            child_ids: list[int] = [cid]
            children = await self._cat_repo.get_children(cid)
            child_ids.extend(c.id for c in children if c.id is not None)

            actual_stmt = select(sa_func.sum(WorkHour.hours)).where(
                WorkHour.report_date >= ms,
                WorkHour.report_date <= me,
                WorkHour.category_id.in_(child_ids) if len(child_ids) > 1 else WorkHour.category_id == cid,  # type: ignore[union-attr]
            )
            actual_result = await self._wh_repo._session.exec(actual_stmt)
            actual_val = actual_result.first()
            actual_total = float(str(actual_val if actual_val is not None else 0))

            # 归入季度
            if ym.startswith("2026-01") or ym.startswith("2026-02") or ym.startswith("2026-03") or "Q1" in ym:
                q = "2026-Q1"
            else:
                q = "2026-Q2"

            if cid not in Q_map[q]:
                Q_map[q][cid] = {"plan": 0.0, "actual": 0.0, "cat_name": cat_name}
            Q_map[q][cid]["plan"] = float(str(Q_map[q][cid]["plan"])) + plan.plan_days  # type: ignore[operator]
            Q_map[q][cid]["actual"] = float(str(Q_map[q][cid]["actual"])) + actual_total  # type: ignore[operator]

        result: list[dict[str, object]] = []
        for q in ["2026-Q1", "2026-Q2"]:
            for cid, v in Q_map[q].items():
                plan_total = float(str(v["plan"]))
                actual_total = float(str(v["actual"]))
                deviation = actual_total - plan_total
                rate = round(actual_total / plan_total * 100, 1) if plan_total > 0 else 0.0
                result.append({
                    "quarter": q,
                    "category_name": v["cat_name"],
                    "category_id": cid,
                    "plan_days": round(plan_total, 1),
                    "actual_days": round(actual_total, 1),
                    "deviation": round(deviation, 1),
                    "achieve_rate": rate,
                })
        return result


    async def get_person_category(
        self,
        time_period: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
        category_level: int = 1,
    ) -> list[dict[str, object]]:
        """人员 x 分类 交叉, 每人按分类汇总分布。"""
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        from app.services.capacity_audit_service import CapacityAuditService

        audit_svc = CapacityAuditService(self._emp_repo, self._wh_repo, self._cap_repo)
        emp_ids = await audit_svc._resolve_employee_ids(dept_level, dept_name, role)

        return await self._wh_repo.aggregate_by_person_with_category(
            start_date, end_date, category_level, emp_ids
        )

    async def get_matrix(
        self,
        time_period: str | None = None,
        row_dimension: str = "dept",
        col_dimension: str = "category",
        category_level: int = 1,
    ) -> dict[str, object]:
        """综合交叉矩阵。"""
        if row_dimension == "dept":
            return await self.get_dept_category_matrix(time_period, 2, category_level)
        # role 维度
        data = await self.get_role_category(time_period, None, None, category_level)
        roles = [str(r.get("role", "")) for r in data]
        categories = ["三快类", "研发类", "周期类"]
        matrix: list[list[float]] = []
        for role_data in data:
            total = float(str(role_data.get("total_days", 0)))
            row = [total if i == 0 else 0.0 for i in range(len(categories))]
            matrix.append(row)
        return {"depts": roles, "categories": categories, "matrix": matrix}


def _month_to_quarter(month: str) -> str:
    """月份 -> 季度标签。"""
    m = int(month[5:7])
    if m <= 3:
        return "2026-Q1"
    elif m <= 6:
        return "2026-Q2"
    return month
