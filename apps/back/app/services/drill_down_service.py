"""数据穿透服务: 逐层下钻, 按维度路径返回明细。"""

from datetime import date

from app.repositories.employee_repository import EmployeeRepository
from app.repositories.project_category_repository import ProjectCategoryRepository
from app.repositories.work_hour_repository import WorkHourRepository
from app.services.capacity_audit_service import _parse_year_months, _year_month_to_date_range


class DrillDownService:
    """数据穿透(下钻)服务: 通用记录查询、部门子节点、分类项目列表。"""

    def __init__(
        self,
        work_hour_repo: WorkHourRepository,
        employee_repo: EmployeeRepository,
        category_repo: ProjectCategoryRepository,
    ) -> None:
        self._wh_repo = work_hour_repo
        self._emp_repo = employee_repo
        self._cat_repo = category_repo

    async def get_records(
        self,
        employee_id: int | None = None,
        project_name: str | None = None,
        time_period: str | None = None,
        category_id: int | None = None,
        dept_path: str | None = None,
        dept_level: int | None = None,
        role: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, object]]:
        """通用下钻: 工时明细记录。至少提供一个筛选条件。"""
        start_date: date | None = None
        end_date: date | None = None
        if time_period:
            year_months = _parse_year_months(time_period)
            start_date, end_date = _year_month_to_date_range(year_months)

        # dept_path -> resolve employee_ids
        employee_ids: list[int] | None = None
        if dept_path and dept_level:
            # dept_path like "产品研发中心/前端组", split and get last segment as dept_name
            parts = [p.strip() for p in dept_path.split("/") if p.strip()]
            dept_name = parts[-1] if parts else dept_path
            employees = await self._emp_repo.list_by_department(dept_level, dept_name)
            employee_ids = [e.id for e in employees if e.id is not None]
        elif role:
            # Resolve by role
            employees = await self._emp_repo.list_active_normal()
            employee_ids = [e.id for e in employees if e.role == role and e.id is not None]
        elif dept_level and not dept_path:
            # Just dept_level filter without dept_name: use the filter options approach
            # This case is mostly covered by role-only filter above
            pass

        records = await self._wh_repo.get_records(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            project_name=project_name,
            category_id=category_id,
            employee_ids=employee_ids,
            limit=limit,
        )

        result: list[dict[str, object]] = []
        for wh in records:
            result.append(
                {
                    "id": wh.id,
                    "project_name": wh.project_name,
                    "matched_project_name": wh.matched_project_name,
                    "reporter": wh.reporter,
                    "reporter_department": wh.reporter_department,
                    "report_date": wh.report_date.isoformat() if wh.report_date else None,
                    "hours": wh.hours,
                    "description": wh.description,
                    "category_path": "",
                    "employee_id": wh.employee_id,
                }
            )
        return result

    async def get_dept_children(
        self,
        time_period: str | None = None,
        parent_dept: str | None = None,
        dept_level: int = 2,
    ) -> list[dict[str, object]]:
        """部门下钻: 获取某部门的子部门列表。"""
        if not parent_dept:
            dept_names = await self._emp_repo.list_departments(dept_level)
        else:
            dept_names = await self._emp_repo.list_departments(dept_level)

        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        result: list[dict[str, object]] = []
        for dept_name in dept_names:
            # 该部门下的人员 id
            employees = await self._emp_repo.list_by_department(dept_level, dept_name)
            emp_ids = [e.id for e in employees if e.id is not None]

            # 实际工时
            actual_rows = await self._wh_repo.aggregate_by_person_and_category(start_date, end_date, emp_ids)
            actual_days = sum(float(str(r.get("actual_days", 0))) for r in actual_rows)

            # 是否有子节点(下钻到更深层级)
            has_children = dept_level < 4

            result.append(
                {
                    "dept_name": dept_name,
                    "dept_path": (parent_dept + "/" + dept_name) if parent_dept else dept_name,
                    "dept_level": dept_level,
                    "person_count": len(emp_ids),
                    "total_actual_days": round(actual_days, 1),
                    "has_children": has_children,
                }
            )

        result.sort(key=lambda x: float(str(x["total_actual_days"])), reverse=True)  # type: ignore[arg-type]
        return result

    async def get_monthly_persons(
        self,
        month: str | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, object]]:
        """月度人员明细下钻: 筛选某月下的人员列表。"""
        if not month:
            return []
        return await self._wh_repo.aggregate_monthly_persons(
            month=month,
            dept_level=dept_level,
            dept_name=dept_name,
            role=role,
        )

    async def get_cell_persons(
        self,
        time_period: str | None = None,
        category_id: int | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, object]]:
        """交叉单元格下钻: 部门+分类/角色+分类 -> 人员列表。"""
        if not category_id:
            return []
        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)
        return await self._wh_repo.aggregate_cell_persons(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            dept_level=dept_level,
            dept_name=dept_name,
            role=role,
        )

    async def get_category_projects(
        self,
        time_period: str | None = None,
        category_id: int | None = None,
        dept_level: int | None = None,
        dept_name: str | None = None,
        role: str | None = None,
    ) -> list[dict[str, object]]:
        """分类下钻: 获取某分类下的项目列表。"""
        if not category_id:
            return []

        year_months = _parse_year_months(time_period)
        start_date, end_date = _year_month_to_date_range(year_months)

        # 这里需要构造 audit service 以复用 resolve_employee_ids

        emp_ids: list[int] | None = None
        if dept_level and dept_name:
            employees = await self._emp_repo.list_by_department(dept_level, dept_name)
            emp_ids = [e.id for e in employees if e.id is not None]
        elif role:
            employees = await self._emp_repo.list_active_normal()
            emp_ids = [e.id for e in employees if e.role == role and e.id is not None]

        projects = await self._wh_repo.get_projects_by_category(category_id, start_date, end_date, emp_ids)

        total_days = sum(float(str(p.get("person_days", 0))) for p in projects)

        result: list[dict[str, object]] = []
        for p in projects:
            person_days = float(str(p.get("person_days", 0)))
            person_count = int(float(str(p.get("person_count", 0))))
            percentage = round(person_days / total_days * 100, 1) if total_days > 0 else 0.0
            result.append(
                {
                    "project_name": p.get("project_name", ""),
                    "person_days": round(person_days, 1),
                    "person_count": person_count,
                    "percentage": percentage,
                }
            )
        return result
