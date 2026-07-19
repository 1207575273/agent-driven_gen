"""数据导入服务: 编排导入流程(清空 -> 导入 -> 匹配 -> 计算)。"""

from datetime import date

from app.datasources.base import DataSourceProvider
from app.repositories.data_import_repository import DataImportRepository
from app.services.project_matching_engine import (
    build_category_map,
    clean_project_name,
    match_to_category,
)
from app.services.should_be_capacity_engine import calculate_all as calculate_all_capacity
from app.services.should_be_capacity_engine import get_h1_months


class DataImportService:
    """编排全量数据导入流程。

    导入顺序:
    1. 清空所有业务表
    2. 导入花名册
    3. 导入项目分类
    4. 导入节假日
    5. 导入工时明细(含人员匹配 + 项目匹配)
    6. 计算并导入应有产能
    7. 导入三快计划(可选)
    """

    def __init__(self, repository: DataImportRepository) -> None:
        self._repo = repository

    async def import_all(self, provider: DataSourceProvider) -> dict[str, object]:
        """执行全量导入。

        Returns:
            dict: 导入统计 {success, stats: {employees, work_hours, categories, holidays, capacity, plans,
                   employee_match_rate, project_match_rate, unmatched_projects, errors}}
        """
        stats: dict[str, object] = {
            "employees_imported": 0,
            "work_hours_imported": 0,
            "categories_imported": 0,
            "holidays_imported": 0,
            "capacity_records_created": 0,
            "plans_imported": 0,
            "employee_match_rate": 0.0,
            "project_match_rate": 0.0,
            "unmatched_projects": [],
            "unmatched_employees": [],
            "errors": [],
        }

        try:
            # 1. 清空
            await self._repo.clear_all()

            # 2. 导入花名册
            employee_data = list(provider.provide_employees())
            await self._repo.bulk_insert_employees(employee_data)
            stats["employees_imported"] = len(employee_data)

            # 3. 导入项目分类
            cat_data = provider.provide_project_categories()
            cats_saved = await self._repo.bulk_insert_project_categories(cat_data)
            stats["categories_imported"] = len(cats_saved)

            # 构建分类映射(用于后续项目匹配)
            category_map = build_category_map(cats_saved)

            # 4. 导入节假日
            holiday_data = provider.provide_holidays()
            stats["holidays_imported"] = await self._repo.bulk_insert_holidays(holiday_data)

            # 5. 获取员工映射(工号/姓名 -> employee_id)
            employee_map = await self._repo.get_employees_map()

            # 6. 逐行处理工时: 人员匹配 + 项目匹配 + 批量写入
            work_hours_input = list(provider.provide_work_hours())
            matched_count = 0
            project_matched_count = 0
            unmatched_projects_set: set[str] = set()
            processed_rows: list[dict[str, object]] = []

            for wh_row in work_hours_input:
                # 人员匹配: 通过填报人(去_sz后缀) 匹配花名册
                reporter = str(wh_row.get("reporter", ""))
                reporter_dept = str(wh_row.get("reporter_department", ""))
                matched_emp_id = _match_person(reporter, employee_map, reporter_dept)

                # 项目匹配: 清洗项目名 + 匹配分类
                raw_project = str(wh_row.get("project_name", ""))
                cleaned = clean_project_name(raw_project)
                cat_id = match_to_category(cleaned, category_map)

                if cat_id is not None:
                    project_matched_count += 1
                else:
                    unmatched_projects_set.add(cleaned)

                if matched_emp_id is not None:
                    matched_count += 1

                processed_rows.append(
                    {
                        "project_name": raw_project,
                        "reporter": reporter,
                        "reporter_department": wh_row.get("reporter_department"),
                        "creator": wh_row.get("creator"),
                        "report_date": wh_row.get("report_date"),
                        "hours": wh_row.get("hours", 0.0),
                        "description": wh_row.get("description"),
                        "employee_id": matched_emp_id,
                        "matched_project_name": cleaned,
                        "category_id": cat_id,
                    }
                )

            # 批量插入工时
            stats["work_hours_imported"] = await self._repo.bulk_insert_work_hours(processed_rows)

            # 计算匹配率
            total = len(work_hours_input)
            stats["employee_match_rate"] = round(matched_count / total * 100, 1) if total > 0 else 0.0
            stats["project_match_rate"] = round(project_matched_count / total * 100, 1) if total > 0 else 0.0
            stats["unmatched_projects"] = sorted(unmatched_projects_set)

            # 7. 计算应有产能
            # 将 employee_data 转为带 id 的 list(要重建映射, 因为 bulk_insert_employees 会 flush)
            emp_map = await self._repo.get_employees_map()
            employees_for_capacity: list[dict[str, object]] = []
            for emp_row in employee_data:
                emp_id_str = str(emp_row.get("employee_id", ""))
                emp_name = str(emp_row.get("name", ""))
                emp_db_id = emp_map.get(emp_id_str) or emp_map.get(emp_name)
                if emp_db_id is not None:
                    employees_for_capacity.append(
                        {
                            "id": emp_db_id,
                            "employee_id": emp_row.get("employee_id"),
                            "name": emp_name,
                            "entry_date": emp_row.get("entry_date"),
                            "leave_date": emp_row.get("leave_date"),
                            "employee_status": emp_row.get("employee_status"),
                            "is_excluded": emp_row.get("is_excluded"),
                        }
                    )

            # 构建假日/补班集合
            holiday_set: set[date] = set()
            makeup_set: set[date] = set()
            for h in holiday_data:
                d = h.get("holiday_date")
                if isinstance(d, date):
                    if h.get("is_workday"):
                        makeup_set.add(d)
                    else:
                        holiday_set.add(d)

            # 计算
            months = get_h1_months()
            capacity_records = calculate_all_capacity(employees_for_capacity, months, holiday_set, makeup_set)
            stats["capacity_records_created"] = await self._repo.bulk_insert_should_be_capacity(capacity_records)

            # 8. 导入三快计划(可选)
            plan_data = provider.provide_three_fast_plans()
            if plan_data:
                cat_by_name: dict[str, int] = {}
                for cat in cats_saved:
                    cn = str(cat.get("category_name", ""))
                    cid = cat.get("id")
                    if cn and cid is not None:
                        cat_by_name[cn] = int(float(str(cid)))
                plans_with_id: list[dict[str, object]] = []
                for p in plan_data:
                    cn = str(p.get("category_name", ""))
                    cid = cat_by_name.get(cn)
                    if cid is not None:
                        plans_with_id.append(
                            {
                                "plan_quarter": p.get("plan_quarter"),
                                "category_id": cid,
                                "plan_days": p.get("plan_days"),
                            }
                        )
                stats["plans_imported"] = await self._repo.bulk_insert_three_fast_plans(plans_with_id)

            return {"success": True, "stats": stats}

        except Exception as e:
            errors = stats.get("errors")
            if isinstance(errors, list):
                errors.append(str(e))
            return {"success": False, "stats": stats, "error": str(e)}

    async def rematch_categories(self) -> dict[str, object]:
        """重新执行项目匹配(不重新导入数据)。

        当项目分类配置更新后调用, 重新清洗+匹配所有工时记录的项目分类。
        """
        # 获取当前所有分类
        cats = await self._repo.get_all_categories()
        category_map = build_category_map(cats)

        # 获取所有工时记录
        wh_rows = await self._repo.get_all_work_hours_brief()

        unmatched_count = 0
        unmatched_projects_set: set[str] = set()
        updates: list[dict[str, object]] = []

        for wh in wh_rows:
            project_name = str(wh.get("matched_project_name", ""))
            cat_id = match_to_category(project_name, category_map) if project_name else None

            if cat_id is None:
                unmatched_count += 1
                if project_name:
                    unmatched_projects_set.add(project_name)

            if cat_id != wh.get("category_id"):
                updates.append({"id": wh["id"], "category_id": cat_id})

        if updates:
            await self._repo.update_work_hour_category_batch(updates)

        return {
            "success": True,
            "rematched_count": len(wh_rows),
            "updated_count": len(updates),
            "unmatched_count": unmatched_count,
            "unmatched_projects": sorted(unmatched_projects_set),
        }


def _match_person(reporter: str, employee_map: dict[str, int], reporter_department: str = "") -> int | None:
    """将填报人名匹配到 employee_id。
    匹配策略:
    1. 去 _sz 后缀 -> 精确匹配姓名
    2. 重名(如陈鹏): 按填报部门+姓名组合键匹配
    3. 返回 None 表示未匹配
    """
    if not reporter:
        return None
    # 去 _sz 后缀
    name_no_sz = reporter.replace("_sz", "").replace("_SZ", "")
    # 组合键: 姓名_填报部门 (用于区分重名)
    if reporter_department:
        dept_key = f"{name_no_sz}__{reporter_department}"
        if dept_key in employee_map:
            return employee_map[dept_key]
    # 直接匹配
    if name_no_sz in employee_map:
        return employee_map[name_no_sz]
    if reporter in employee_map:
        return employee_map[reporter]
    return None
