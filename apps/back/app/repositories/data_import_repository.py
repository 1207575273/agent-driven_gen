"""DataImport 仓储层(DAO): 批量导入落库 + 清空表。"""

from sqlmodel import delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.holiday import Holiday
from app.models.project_category import ProjectCategory
from app.models.should_be_capacity import ShouldBeCapacity
from app.models.three_fast_plan import ThreeFastPlan
from app.models.work_hour import WorkHour

_EMPLOYEE_ID_CACHE: dict[str, int] = {}
BATCH_SIZE = 1000


class DataImportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def clear_all(self) -> None:
        tables_in_order = [WorkHour, ShouldBeCapacity, ThreeFastPlan, Holiday, Employee, ProjectCategory]
        for table in tables_in_order:
            await self._session.exec(delete(table))  # type: ignore[arg-type]
        await self._session.flush()
        _EMPLOYEE_ID_CACHE.clear()

    async def bulk_insert_employees(self, data: list[dict[str, object]]) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        batch: list[Employee] = []
        for _i, row in enumerate(data):
            emp = Employee(
                name=str(row.get("name", "")),
                employee_id=_safe_str(row.get("employee_id")),
                position=_safe_str(row.get("position")),
                level1_dept=_safe_str(row.get("level1_dept")),
                level2_dept=_safe_str(row.get("level2_dept")),
                level3_dept=_safe_str(row.get("level3_dept")),
                level4_dept=_safe_str(row.get("level4_dept")),
                actual_team=_safe_str(row.get("actual_team")),
                role=_safe_str(row.get("role")),
                employee_type=_safe_str(row.get("employee_type")),
                employee_status=_safe_str(row.get("employee_status")),
                position_type=_safe_str(row.get("position_type")),
                is_excluded=bool(row.get("is_excluded")),
            )
            # Handle date fields
            entry = row.get("entry_date")
            leave = row.get("leave_date")
            if entry is not None:
                from datetime import date as date_type

                if isinstance(entry, date_type):
                    emp.entry_date = entry
            if leave is not None:
                from datetime import date as date_type

                if isinstance(leave, date_type):
                    emp.leave_date = leave
            emp.fill_note = _safe_str(row.get("fill_note"))
            emp.remarks = _safe_str(row.get("remarks"))
            emp.planned_project1 = _safe_str(row.get("planned_project1"))
            emp.planned_project2 = _safe_str(row.get("planned_project2"))
            emp.planned_project3 = _safe_str(row.get("planned_project3"))
            emp.planned_project4 = _safe_str(row.get("planned_project4"))
            emp.planned_project5 = _safe_str(row.get("planned_project5"))
            batch.append(emp)
            if len(batch) >= BATCH_SIZE:
                self._session.add_all(batch)
                await self._session.flush()
                batch = []
        if batch:
            self._session.add_all(batch)
            await self._session.flush()
        return results

    async def bulk_insert_work_hours(self, data: list[dict[str, object]]) -> int:
        count = 0
        batch: list[WorkHour] = []
        for row in data:
            wh = WorkHour(
                project_name=str(row.get("project_name", "")),
                reporter=str(row.get("reporter", "")),
                reporter_department=_safe_str(row.get("reporter_department")),
                creator=_safe_str(row.get("creator")),
                hours=float(str(row.get("hours", 0.0))),
                description=_safe_str(row.get("description")),
                employee_id=_safe_int(row.get("employee_id")),
                matched_project_name=_safe_str(row.get("matched_project_name")),
                category_id=_safe_int(row.get("category_id")),
            )
            report_date = row.get("report_date")
            if report_date is not None:
                from datetime import date as date_type

                if isinstance(report_date, date_type):
                    wh.report_date = report_date
            batch.append(wh)
            if len(batch) >= BATCH_SIZE:
                self._session.add_all(batch)
                await self._session.flush()
                count += len(batch)
                batch = []
        if batch:
            self._session.add_all(batch)
            await self._session.flush()
            count += len(batch)
        return count

    async def bulk_insert_project_categories(self, data: list[dict[str, object]]) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for row in data:
            cat_level = int(float(str(row.get("category_level", 1))))
            # level=0 是项目名, 不插入分类表, 但需返回(parent_id -> category_id 映射)
            if cat_level == 0:
                parent_id = row.get("parent_id")
                results.append(
                    {
                        "id": int(float(str(parent_id))) if parent_id is not None else 0,
                        "category_name": str(row.get("category_name", "")),
                        "category_level": 0,
                        "parent_id": int(float(str(parent_id))) if parent_id is not None else None,
                        "sort_order": 0,
                    }
                )
                continue
            cat = ProjectCategory(
                category_name=str(row.get("category_name", "")),
                category_level=cat_level,
                parent_id=_safe_int(row.get("parent_id")),
                sort_order=int(float(str(row.get("sort_order", 0)))),
            )
            self._session.add(cat)
            await self._session.flush()
            results.append(
                {
                    "id": cat.id,
                    "category_name": cat.category_name,
                    "category_level": cat.category_level,
                    "parent_id": cat.parent_id,
                    "sort_order": cat.sort_order,
                }
            )
        return results

    async def bulk_insert_holidays(self, data: list[dict[str, object]]) -> int:
        count = 0
        for row in data:
            holiday_date = row.get("holiday_date")
            if holiday_date is None:
                continue
            from datetime import date as date_type

            if not isinstance(holiday_date, date_type):
                continue
            h = Holiday(
                holiday_name=str(row.get("holiday_name", "")),
                is_workday=bool(row.get("is_workday")),
                holiday_date=holiday_date,
            )
            self._session.add(h)
            count += 1
        await self._session.flush()
        return count

    async def bulk_insert_should_be_capacity(self, data: list[dict[str, object]]) -> int:
        count = 0
        batch: list[ShouldBeCapacity] = []
        for row in data:
            sbc = ShouldBeCapacity(
                employee_id=int(float(str(row["employee_id"]))),
                year_month=str(row["year_month"]),
                total_working_days=int(float(str(row["total_working_days"]))),
                active_working_days=int(float(str(row["active_working_days"]))),
                capacity_days=float(str(row["capacity_days"])),
            )
            batch.append(sbc)
            if len(batch) >= BATCH_SIZE:
                self._session.add_all(batch)
                await self._session.flush()
                count += len(batch)
                batch = []
        if batch:
            self._session.add_all(batch)
            await self._session.flush()
            count += len(batch)
        return count

    async def bulk_insert_three_fast_plans(self, data: list[dict[str, object]]) -> int:
        count = 0
        for row in data:
            tfp = ThreeFastPlan(
                plan_quarter=str(row.get("plan_quarter", "")),
                category_id=int(float(str(row["category_id"]))),
                plan_days=float(str(row["plan_days"])),
            )
            self._session.add(tfp)
            count += 1
        await self._session.flush()
        return count

    async def get_employees_map(self) -> dict[str, int]:
        if _EMPLOYEE_ID_CACHE:
            return dict(_EMPLOYEE_ID_CACHE)
        from sqlmodel import select as sm_select

        result = await self._session.exec(sm_select(Employee))
        for emp in result.all():
            eid = emp.id
            if eid is None:
                continue
            if emp.employee_id:
                _EMPLOYEE_ID_CACHE[emp.employee_id] = eid
            name_without_sz = emp.name.replace("_sz", "")
            if name_without_sz != emp.name:
                _EMPLOYEE_ID_CACHE[name_without_sz] = eid
            if emp.name not in _EMPLOYEE_ID_CACHE:
                _EMPLOYEE_ID_CACHE[emp.name] = eid
            # 重名处理: 从备注中解析填报部门和别名
            remarks = emp.remarks or ""
            if remarks:
                import re as _re
                # 工时系统别名: xxx (外包用 _sz 后缀, 已在前面处理了去 _sz 匹配)
                m = _re.findall(r'工时系统别名:([^;]+)', remarks)
                for alias in m:
                    a = alias.strip()
                    if a and a not in _EMPLOYEE_ID_CACHE:
                        _EMPLOYEE_ID_CACHE[a] = eid
                # 填报部门匹配: 备注中有"填报部门是xxx的"说明
                m2 = _re.findall(r'填报部门是(.+?)的', remarks)
                for dept in m2:
                    key = f"{emp.name}__{dept.strip()}"
                    if key not in _EMPLOYEE_ID_CACHE:
                        _EMPLOYEE_ID_CACHE[key] = eid
                    # 备注末尾的人名可能是工时中使用的名字
                    name_match = _re.search(r'的(.+)$', remarks)
                    if name_match:
                        alt_name = name_match.group(1).strip()
                        alt_key = f"{alt_name}__{dept.strip()}"
                        if alt_key not in _EMPLOYEE_ID_CACHE:
                            _EMPLOYEE_ID_CACHE[alt_key] = eid
        return dict(_EMPLOYEE_ID_CACHE)

    async def update_work_hour_category_batch(self, updates: list[dict[str, object]]) -> int:
        from sqlmodel import update as sm_update

        count = 0
        for item in updates:
            wh_id = int(float(str(item["id"])))
            cat_id = _safe_int(item.get("category_id"))
            stmt = sm_update(WorkHour).where(WorkHour.id == wh_id).values(category_id=cat_id)  # type: ignore[arg-type]
            await self._session.exec(stmt)
            count += 1
        await self._session.flush()
        return count

    async def get_all_work_hours_brief(self) -> list[dict[str, object]]:
        from sqlmodel import select as sm_select

        result = await self._session.exec(sm_select(WorkHour))
        return [
            {"id": wh.id, "matched_project_name": wh.matched_project_name, "category_id": wh.category_id}
            for wh in result.all()
        ]

    async def get_all_categories(self) -> list[dict[str, object]]:
        from sqlmodel import select as sm_select

        result = await self._session.exec(sm_select(ProjectCategory))
        return [
            {
                "id": cat.id,
                "category_name": cat.category_name,
                "category_level": cat.category_level,
                "parent_id": cat.parent_id,
            }
            for cat in result.all()
        ]


def _safe_str(value: object) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    return s if s else None


def _safe_int(value: object) -> int | None:
    if value is None:
        return None
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None
