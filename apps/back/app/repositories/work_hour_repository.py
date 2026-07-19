"""工时仓储层(Repository / DAO): 封装工时数据的所有聚合查询。

持有 AsyncSession, 只做数据访问, 不包含业务逻辑。
"""

from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
from app.models.project_category import ProjectCategory
from app.models.work_hour import WorkHour

# 常量: 部门列映射
DEPT_COL_NAMES: dict[int, str] = {2: "level2_dept", 3: "level3_dept"}


class WorkHourRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # 聚合查询: 按项目分组
    # ------------------------------------------------------------------
    async def aggregate_by_project(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
        role: str | None = None,
        personnel_type: str | None = None,
        project_name: str | None = None,
    ) -> Sequence[tuple[str, float, int]]:
        """按项目分组统计: project_name, total_days, member_count。"""
        cols = (
            WorkHour.project_name,
            func.sum(WorkHour.hours).label("total_days"),
            func.count(col(WorkHour.reporter).distinct()).label("member_count"),
        )
        base: Any = select(*cols)
        base = self._join_employee_if_needed(base, department, role, personnel_type)
        base = self._apply_common(
            base, start_date, end_date, project_name, department, department_level, role, personnel_type
        )
        base = base.group_by(WorkHour.project_name).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [(str(r[0]), float(r[1] or 0), int(r[2] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按月分组
    # ------------------------------------------------------------------
    async def aggregate_by_month(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
        role: str | None = None,
        personnel_type: str | None = None,
        project_name: str | None = None,
    ) -> Sequence[tuple[str, float]]:
        """按月分组统计人天。"""
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)
        base: Any = select(month_expr.label("month"), func.sum(WorkHour.hours).label("total_days"))
        base = self._join_employee_if_needed(base, department, role, personnel_type)
        base = self._apply_common(
            base, start_date, end_date, project_name, department, department_level, role, personnel_type
        )
        base = base.group_by(month_expr).order_by(month_expr)
        rows = (await self._session.exec(base)).all()
        return [(str(r[0]), float(r[1] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按人分组
    # ------------------------------------------------------------------
    async def aggregate_by_person(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
        role: str | None = None,
        personnel_type: str | None = None,
        project_name: str | None = None,
    ) -> Sequence[tuple[int, str, str, str, float]]:
        """按人分组统计。"""
        # SQLModel 的 InstrumentedAttribute 与 mypy 的 select() overload 存在已知摩擦,
        # 5 参数 select + join .where 模式无法通过 strict check, 此处显式忽略。
        base: Any = select(  # type: ignore[call-overload]
            WorkHour.employee_id,
            Employee.name,
            Employee.role,
            Employee.level2_dept,
            func.sum(WorkHour.hours).label("total_days"),
        ).where(WorkHour.employee_id == Employee.id)
        base = self._apply_common(
            base, start_date, end_date, project_name, department, department_level, role, personnel_type
        )
        base = base.group_by(WorkHour.employee_id).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [(int(r[0] or 0), str(r[1] or ""), str(r[2] or ""), str(r[3] or ""), float(r[4] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按人+项目
    # ------------------------------------------------------------------
    async def aggregate_by_person_project(
        self, employee_id: int, start_date: date | None = None, end_date: date | None = None
    ) -> Sequence[tuple[str, float]]:
        """按人+项目分组。"""
        base: Any = select(WorkHour.project_name, func.sum(WorkHour.hours).label("total_days")).where(
            WorkHour.employee_id == employee_id
        )
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(WorkHour.project_name).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [(str(r[0]), float(r[1] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 某人+项目月度拆分
    # ------------------------------------------------------------------
    async def aggregate_person_project_by_month(
        self, employee_id: int, project_name: str, start_date: date | None = None, end_date: date | None = None
    ) -> Sequence[tuple[str, float]]:
        """某人+项目的月度拆分。"""
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)
        base: Any = (
            select(month_expr.label("month"), func.sum(WorkHour.hours).label("total_days"))
            .where(WorkHour.employee_id == employee_id)
            .where(WorkHour.project_name == project_name)
        )
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(month_expr).order_by(month_expr)
        rows = (await self._session.exec(base)).all()
        return [(str(r[0]), float(r[1] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按角色分组
    # ------------------------------------------------------------------
    async def aggregate_by_role(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
    ) -> Sequence[tuple[str, float, int]]:
        """按角色分组统计。"""
        base: Any = (
            select(
                Employee.role,
                func.sum(WorkHour.hours).label("total_days"),
                func.count(col(WorkHour.employee_id).distinct()).label("person_count"),
            )
            .where(WorkHour.employee_id == Employee.id)
            .where(col(Employee.role).isnot(None))
            .where(col(Employee.role) != "")
        )
        base = self._apply_date_dept(base, start_date, end_date, department, department_level)
        base = base.group_by(Employee.role).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [(str(r[0] or ""), float(r[1] or 0), int(r[2] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按员工状态分组
    # ------------------------------------------------------------------
    async def aggregate_by_status(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
    ) -> Sequence[tuple[str, float, int]]:
        """按员工状态分组。"""
        base: Any = (
            select(
                Employee.employee_status,
                func.sum(WorkHour.hours).label("total_days"),
                func.count(col(WorkHour.employee_id).distinct()).label("person_count"),
            )
            .where(WorkHour.employee_id == Employee.id)
            .where(col(Employee.employee_status).isnot(None))
            .where(col(Employee.employee_status) != "")
        )
        base = self._apply_date_dept(base, start_date, end_date, department, department_level)
        base = base.group_by(Employee.employee_status)
        rows = (await self._session.exec(base)).all()
        return [(str(r[0] or ""), float(r[1] or 0), int(r[2] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 角色+部门分布
    # ------------------------------------------------------------------
    async def aggregate_role_dept_distribution(
        self,
        role: str,
        start_date: date | None = None,
        end_date: date | None = None,
        department: str | None = None,
        department_level: int = 2,
    ) -> Sequence[tuple[str, int, float]]:
        """某个角色的部门分布。"""
        dept_col = getattr(Employee, DEPT_COL_NAMES.get(department_level, "level2_dept"))

        base: Any = (
            select(
                dept_col,
                func.count(col(WorkHour.employee_id).distinct()).label("person_count"),
                func.sum(WorkHour.hours).label("total_days"),
            )
            .where(WorkHour.employee_id == Employee.id)
            .where(Employee.role == role)
            .where(col(dept_col).isnot(None))
            .where(col(dept_col) != "")
        )
        base = self._apply_date_dept(base, start_date, end_date, department, department_level)
        base = base.group_by(dept_col).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [(str(r[0] or ""), int(r[1] or 0), float(r[2] or 0)) for r in rows]

    # ------------------------------------------------------------------
    # 聚合查询: 按人+分类(人员汇总, 不含分类分布)
    # ------------------------------------------------------------------
    async def aggregate_by_person_and_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """按人员汇总: 返回每个人的基本信息+实际人天+项目数。"""
        cols: list[Any] = [
            WorkHour.employee_id,
            func.max(Employee.name).label("name"),
            func.max(Employee.employee_id).label("employee_id_str"),
            func.max(Employee.level2_dept).label("dept_name"),
            func.max(Employee.level2_dept).label("dept_path"),
            func.max(Employee.role).label("role"),
            func.sum(WorkHour.hours).label("actual_days"),
            func.count(col(WorkHour.project_name).distinct()).label("project_count"),
        ]
        base: Any = select(*cols).where(WorkHour.employee_id == Employee.id)  # type: ignore[call-overload]
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(WorkHour.employee_id)
        rows = (await self._session.exec(base)).all()
        return [
            {
                "employee_id": int(float(str(r[0] or 0))),
                "name": str(r[1] or ""),
                "employee_id_str": str(r[2] or ""),
                "dept_name": str(r[3] or ""),
                "dept_path": str(r[4] or ""),
                "role": str(r[5] or ""),
                "actual_days": round(float(str(r[6] or 0)), 1),
                "project_count": int(float(str(r[7] or 0))),
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 人员月度明细
    # ------------------------------------------------------------------
    async def aggregate_by_person_month(
        self,
        employee_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, object]]:
        """单人按月聚合工时。"""
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)
        base: Any = select(
            month_expr.label("month"),
            func.sum(WorkHour.hours).label("actual_days"),
        ).where(WorkHour.employee_id == employee_id)
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(month_expr).order_by(month_expr)
        rows = (await self._session.exec(base)).all()
        return [
            {"month": str(r[0]), "actual_days": round(float(str(r[1] or 0)), 1)}
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 人员项目投入(含分类信息)
    # ------------------------------------------------------------------
    async def get_person_projects(
        self,
        employee_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, object]]:
        """单人按项目聚合, 含分类信息。"""
        cols: list[Any] = [
            WorkHour.project_name,
            func.sum(WorkHour.hours).label("person_days"),
            func.max(ProjectCategory.category_name).label("category_name"),
            func.max(WorkHour.category_id).label("category_id"),
        ]
        base: Any = (
            select(*cols)  # type: ignore[call-overload]
            .where(WorkHour.employee_id == employee_id)
            .outerjoin(ProjectCategory, WorkHour.category_id == ProjectCategory.id)
        )
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(WorkHour.project_name).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [
            {
                "project_name": str(r[0] or ""),
                "person_days": round(float(str(r[1] or 0)), 1),
                "category_name": str(r[2] or "未分类"),
                "category_id": int(float(str(r[3]))) if r[3] is not None else None,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 人员排名
    # ------------------------------------------------------------------
    async def rank_by_person(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        employee_ids: list[int] | None = None,
        sort_by: str = "actual_days",
        sort_dir: str = "desc",
    ) -> list[dict[str, object]]:
        """人员排名: 按指定维度排序。"""
        cols: list[Any] = [
            WorkHour.employee_id,
            func.max(Employee.name).label("name"),
            func.max(Employee.employee_id).label("employee_id_str"),
            func.max(Employee.level2_dept).label("dept_name"),
            func.max(Employee.level2_dept).label("dept_path"),
            func.max(Employee.role).label("role"),
            func.sum(WorkHour.hours).label("actual_days"),
            func.count(col(WorkHour.project_name).distinct()).label("project_count"),
        ]
        base: Any = select(*cols).where(WorkHour.employee_id == Employee.id)  # type: ignore[call-overload]
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(WorkHour.employee_id)

        # 动态排序
        sort_map: dict[str, Any] = {
            "actual_days": func.sum(WorkHour.hours),
            "project_count": func.count(col(WorkHour.project_name).distinct()),
            "name": func.max(Employee.name),
        }
        sort_col = sort_map.get(sort_by, func.sum(WorkHour.hours))
        # 三元表达式: sort_dir 控制排序方向
        base = base.order_by(sort_col.asc() if sort_dir == "asc" else sort_col.desc())  # type: ignore[arg-type]

        rows = (await self._session.exec(base)).all()
        return [
            {
                "employee_id": int(float(str(r[0] or 0))),
                "name": str(r[1] or ""),
                "employee_id_str": str(r[2] or ""),
                "dept_name": str(r[3] or ""),
                "dept_path": str(r[4] or ""),
                "role": str(r[5] or ""),
                "actual_days": round(float(str(r[6] or 0)), 1),
                "project_count": int(float(str(r[7] or 0))),
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 时间 x 分类(祖先追溯)
    # ------------------------------------------------------------------
    async def aggregate_by_time_and_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        category_level: int = 1,
        parent_category_id: int | None = None,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """时间(月) x 分类 交叉聚合, 祖先追溯。"""
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)
        # 查询所有 L3 叶子分类 + 构建祖先映射
        ancestor_map = await self._build_ancestor_map(category_level, parent_category_id)

        cols: list[Any] = [
            month_expr.label("month"),
            WorkHour.category_id,
            func.sum(WorkHour.hours).label("person_days"),
        ]
        base: Any = select(*cols).where(col(WorkHour.category_id).isnot(None))  # type: ignore[call-overload,union-attr]
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(month_expr, WorkHour.category_id)
        rows = (await self._session.exec(base)).all()

        # 祖先追溯 + 聚合
        result_map: dict[str, dict[str, float]] = {}
        for r in rows:
            month = str(r[0])
            cat_id = int(float(str(r[1])))
            days = float(str(r[2] or 0))
            ancestor_name = ancestor_map.get(cat_id, "未分类")
            if month not in result_map:
                result_map[month] = {}
            result_map[month][ancestor_name] = result_map[month].get(ancestor_name, 0.0) + days

        return [
            {"month": m, "category_name": c, "person_days": round(d, 1)}
            for m, cats in sorted(result_map.items())
            for c, d in sorted(cats.items())
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 部门 x 分类(祖先追溯)
    # ------------------------------------------------------------------
    async def aggregate_by_dept_and_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        dept_level: int = 2,
        category_level: int = 1,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """部门 x 分类 交叉聚合, 祖先追溯。"""
        ancestor_map = await self._build_ancestor_map(category_level)
        _dept_col_map: dict[int, str] = {1: "level1_dept", 2: "level2_dept", 3: "level3_dept", 4: "level4_dept"}
        dept_col_name = _dept_col_map.get(dept_level, "level2_dept")
        dept_col = getattr(Employee, dept_col_name)

        cols: list[Any] = [
            dept_col.label("dept_name"),
            WorkHour.category_id,
            func.sum(WorkHour.hours).label("person_days"),
        ]
        base: Any = (
            select(*cols)  # type: ignore[call-overload]
            .where(WorkHour.employee_id == Employee.id)
            .where(col(WorkHour.category_id).isnot(None))
            .where(col(dept_col).isnot(None))
            .where(col(dept_col) != "")
        )
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(dept_col, WorkHour.category_id)
        rows = (await self._session.exec(base)).all()

        result_map: dict[str, dict[str, float]] = {}
        for r in rows:
            dept = str(r[0] or "")
            cat_id = int(float(str(r[1])))
            days = float(str(r[2] or 0))
            ancestor_name = ancestor_map.get(cat_id, "未分类")
            if dept not in result_map:
                result_map[dept] = {}
            result_map[dept][ancestor_name] = result_map[dept].get(ancestor_name, 0.0) + days

        return [
            {"dept_name": d, "category_name": c, "person_days": round(v, 1)}
            for d, cats in sorted(result_map.items())
            for c, v in sorted(cats.items())
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 角色 x 分类(祖先追溯)
    # ------------------------------------------------------------------
    async def aggregate_by_role_and_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        category_level: int = 1,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """角色 x 分类 交叉聚合, 祖先追溯。"""
        ancestor_map = await self._build_ancestor_map(category_level)

        cols: list[Any] = [
            Employee.role,
            WorkHour.category_id,
            func.sum(WorkHour.hours).label("person_days"),
            func.count(col(WorkHour.employee_id).distinct()).label("person_count"),
        ]
        base: Any = (
            select(*cols)  # type: ignore[call-overload]
            .where(WorkHour.employee_id == Employee.id)
            .where(col(WorkHour.category_id).isnot(None))
            .where(col(Employee.role).isnot(None))
            .where(col(Employee.role) != "")
        )
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(Employee.role, WorkHour.category_id)
        rows = (await self._session.exec(base)).all()

        result_map: dict[str, dict[str, object]] = {}  # role -> {cat: days, _pc_cat: cnt}
        role_pc_max: dict[str, dict[str, int]] = {}
        for r in rows:
            role = str(r[0] or "")
            cat_id = int(float(str(r[1])))
            days = float(str(r[2] or 0))
            cnt = int(float(str(r[3] or 0)))
            ancestor_name = ancestor_map.get(cat_id, "未分类")
            if role not in result_map:
                result_map[role] = {}
                role_pc_max[role] = {}
            cur = float(str(result_map[role].get(ancestor_name, 0.0)))
            result_map[role][ancestor_name] = round(cur + days, 1)
            role_pc_max[role][ancestor_name] = max(role_pc_max[role].get(ancestor_name, 0), cnt)

        result: list[dict[str, object]] = []
        for role in sorted(result_map.keys()):
            for cat in sorted(result_map[role].keys()):
                result.append({
                    "role": role,
                    "category_name": cat,
                    "person_days": result_map[role][cat],
                    "person_count": role_pc_max[role].get(cat, 1),
                })
        return result

    # ------------------------------------------------------------------
    # 聚合查询: 人员 x 分类(祖先追溯, 用于人员维度分析)
    # ------------------------------------------------------------------
    async def aggregate_by_person_with_category(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        category_level: int = 1,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """人员 x 分类 交叉聚合, 含祖先追溯。"""
        ancestor_map = await self._build_ancestor_map(category_level)

        cols: list[Any] = [
            WorkHour.employee_id,
            func.max(Employee.name).label("name"),
            func.max(Employee.employee_id).label("employee_id_str"),
            func.max(Employee.level2_dept).label("dept_name"),
            func.max(Employee.level2_dept).label("dept_path"),
            func.max(Employee.role).label("role"),
            WorkHour.category_id,
            func.sum(WorkHour.hours).label("person_days"),
            func.count(col(WorkHour.project_name).distinct()).label("project_count"),
        ]
        base: Any = (
            select(*cols)  # type: ignore[call-overload]
            .where(WorkHour.employee_id == Employee.id)
            .where(col(WorkHour.category_id).isnot(None))
        )
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(WorkHour.employee_id, WorkHour.category_id)
        rows = (await self._session.exec(base)).all()

        # 按人聚合, 每人的分类分布
        person_map: dict[int, dict[str, object]] = {}
        for r in rows:
            eid = int(float(str(r[0] or 0)))
            cat_id = int(float(str(r[6])))
            days = float(str(r[7] or 0))
            ancestor_name = ancestor_map.get(cat_id, "未分类")
            if eid not in person_map:
                person_map[eid] = {
                    "employee_id": eid,
                    "name": str(r[1] or ""),
                    "employee_id_str": str(r[2] or ""),
                    "dept_name": str(r[3] or ""),
                    "dept_path": str(r[4] or ""),
                    "role": str(r[5] or ""),
                    "total_days": 0.0,
                    "project_count": 0,
                    "category_distribution": {},
                }
            entry = person_map[eid]
            entry["total_days"] = float(str(entry["total_days"])) + days  # type: ignore[operator]
            entry["project_count"] = max(int(float(str(entry["project_count"]))), int(float(str(r[8] or 0))))  # type: ignore[operator]
            dist = entry.get("category_distribution", {})
            if isinstance(dist, dict):
                dist[ancestor_name] = dist.get(ancestor_name, 0.0) + days  # type: ignore[index]

        # 四舍五入
        for entry in person_map.values():
            entry["total_days"] = round(float(str(entry["total_days"])), 1)
            dist = entry.get("category_distribution", {})
            if isinstance(dist, dict):
                for k in list(dist.keys()):
                    dist[k] = round(float(str(dist[k])), 1)  # type: ignore[index]

        return sorted(
            person_map.values(),
            key=lambda x: float(str(x["total_days"])),
            reverse=True,
        )  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # 聚合查询: 部门 x 月
    # ------------------------------------------------------------------
    async def aggregate_by_dept_month(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        dept_level: int = 2,
    ) -> list[dict[str, object]]:
        """部门 x 月 聚合。"""
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)
        _dept_col_map: dict[int, str] = {1: "level1_dept", 2: "level2_dept", 3: "level3_dept", 4: "level4_dept"}
        dept_col_name = _dept_col_map.get(dept_level, "level2_dept")
        dept_col = getattr(Employee, dept_col_name)

        cols: list[Any] = [
            dept_col.label("dept_name"),
            month_expr.label("month"),
            func.sum(WorkHour.hours).label("person_days"),
        ]
        base: Any = (
            select(*cols)  # type: ignore[call-overload]
            .where(WorkHour.employee_id == Employee.id)
            .where(col(dept_col).isnot(None))
            .where(col(dept_col) != "")
        )
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(dept_col, month_expr)
        rows = (await self._session.exec(base)).all()
        return [
            {"dept_name": str(r[0] or ""), "month": str(r[1]), "person_days": round(float(str(r[2] or 0)), 1)}
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 聚合查询: 分类 x 月
    # ------------------------------------------------------------------
    async def aggregate_by_category_and_month(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
        category_level: int = 1,
    ) -> list[dict[str, object]]:
        """分类 x 月 聚合, 祖先追溯。"""
        ancestor_map = await self._build_ancestor_map(category_level)
        month_expr = func.strftime("%Y-%m", WorkHour.report_date)

        cols: list[Any] = [
            month_expr.label("month"),
            WorkHour.category_id,
            func.sum(WorkHour.hours).label("person_days"),
        ]
        base: Any = select(*cols).where(col(WorkHour.category_id).isnot(None))  # type: ignore[call-overload,union-attr]
        base = self._apply_date_range(base, start_date, end_date)
        base = base.group_by(month_expr, WorkHour.category_id)
        rows = (await self._session.exec(base)).all()

        result_map: dict[str, dict[str, float]] = {}
        for r in rows:
            month = str(r[0])
            cat_id = int(float(str(r[1])))
            days = float(str(r[2] or 0))
            ancestor_name = ancestor_map.get(cat_id, "未分类")
            if month not in result_map:
                result_map[month] = {}
            result_map[month][ancestor_name] = result_map[month].get(ancestor_name, 0.0) + days

        return [
            {"month": m, "category_name": c, "person_days": round(d, 1)}
            for m, cats in sorted(result_map.items())
            for c, d in sorted(cats.items())
        ]

    # ------------------------------------------------------------------
    # 下钻: 工时明细记录
    # ------------------------------------------------------------------
    async def get_records(
        self,
        employee_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        project_name: str | None = None,
        category_id: int | None = None,
        limit: int = 500,
    ) -> Sequence[WorkHour]:
        """通用工时明细记录查询。"""
        base: Any = select(WorkHour)
        base = self._apply_date_range(base, start_date, end_date)
        if employee_id is not None:
            base = base.where(WorkHour.employee_id == employee_id)
        if project_name:
            base = base.where(WorkHour.project_name == project_name)
        if category_id is not None:
            base = base.where(WorkHour.category_id == category_id)
        base = base.limit(limit)
        result = await self._session.exec(base)
        return result.all()  # type: ignore[no-any-return]

    # ------------------------------------------------------------------
    # 下钻: 分类下的项目列表
    # ------------------------------------------------------------------
    async def get_projects_by_category(
        self,
        category_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        employee_ids: list[int] | None = None,
    ) -> list[dict[str, object]]:
        """某分类下的项目列表(含人天+人数)。"""
        cols: list[Any] = [
            WorkHour.project_name,
            func.sum(WorkHour.hours).label("person_days"),
            func.count(col(WorkHour.employee_id).distinct()).label("person_count"),
        ]
        base: Any = select(*cols).where(WorkHour.category_id == category_id)  # type: ignore[call-overload]
        base = self._apply_date_range(base, start_date, end_date)
        if employee_ids:
            base = base.where(col(WorkHour.employee_id).in_(employee_ids))
        base = base.group_by(WorkHour.project_name).order_by(func.sum(WorkHour.hours).desc())
        rows = (await self._session.exec(base)).all()
        return [
            {
                "project_name": str(r[0]),
                "person_days": round(float(str(r[1] or 0)), 1),
                "person_count": int(float(str(r[2] or 0))),
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # 去重匹配项目列表
    # ------------------------------------------------------------------
    async def get_distinct_matched_projects(self) -> list[str]:
        """去重匹配项目名列表。"""
        stmt = select(col(WorkHour.matched_project_name).distinct()).where(
            col(WorkHour.matched_project_name).isnot(None)
        )
        result = await self._session.exec(stmt)
        return [str(r) for r in result.all() if r]

    # ------------------------------------------------------------------
    # 内部: 祖先追溯映射 L3叶子id -> target_level祖先名
    # ------------------------------------------------------------------
    async def _build_ancestor_map(
        self, target_level: int, parent_category_id: int | None = None
    ) -> dict[int, str]:
        """构建 {L3叶子category_id: target_level祖先名} 映射。"""
        all_cats = (await self._session.exec(select(ProjectCategory))).all()
        # 先构建 id->node 映射
        cat_by_id: dict[int, ProjectCategory] = {}
        for c in all_cats:
            if c.id is not None:
                cat_by_id[c.id] = c

        # 找到所有 L3 叶子
        leaf_ids = [c.id for c in all_cats if c.category_level == 3 and c.id is not None]

        ancestor_map: dict[int, str] = {}
        for leaf_id in leaf_ids:
            if leaf_id is None:
                continue
            # 向上追溯到 target_level
            current: ProjectCategory | None = cat_by_id.get(leaf_id)
            while current is not None and current.category_level > target_level:
                current = cat_by_id.get(current.parent_id) if current.parent_id else None  # type: ignore[arg-type]
            if current and current.category_level == target_level:
                if parent_category_id is None or current.parent_id == parent_category_id:
                    ancestor_map[leaf_id] = current.category_name
                else:
                    ancestor_map[leaf_id] = "未分类"
            else:
                ancestor_map[leaf_id] = "未分类"
        return ancestor_map

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_date_range(base: Any, start_date: date | None, end_date: date | None) -> Any:
        q = base
        if start_date:
            q = q.where(WorkHour.report_date >= start_date)
        if end_date:
            q = q.where(WorkHour.report_date <= end_date)
        return q

    @staticmethod
    def _apply_date_dept(
        base: Any, start_date: date | None, end_date: date | None, department: str | None, department_level: int
    ) -> Any:
        q = WorkHourRepository._apply_date_range(base, start_date, end_date)
        if department:
            dept_col = getattr(Employee, DEPT_COL_NAMES.get(department_level, "level2_dept"))
            q = q.where(dept_col == department)
        return q

    @staticmethod
    def _join_employee_if_needed(
        base: Any, department: str | None, role: str | None, personnel_type: str | None
    ) -> Any:
        """仅在需要部门/角色/人员类型筛选时才 JOIN employees。"""
        if department or role or personnel_type:
            return base.where(WorkHour.employee_id == Employee.id)
        return base

    @staticmethod
    def _apply_common(
        base: Any,
        start_date: date | None,
        end_date: date | None,
        project_name: str | None,
        department: str | None,
        department_level: int,
        role: str | None,
        personnel_type: str | None,
    ) -> Any:
        q = WorkHourRepository._apply_date_range(base, start_date, end_date)
        if project_name:
            q = q.where(WorkHour.project_name == project_name)
        if department:
            dept_col = getattr(Employee, DEPT_COL_NAMES.get(department_level, "level2_dept"))
            q = q.where(dept_col == department)
        if role:
            q = q.where(col(Employee.role) == role)
        if personnel_type:
            q = WorkHourRepository._apply_personnel_type(q, personnel_type)
        return q

    @staticmethod
    def _apply_personnel_type(base: Any, personnel_type: str) -> Any:
        if personnel_type == "在编":
            return base.where(col(WorkHour.reporter).isnot(None))  # type: ignore[call-overload]
        elif personnel_type == "外部人力资源":
            return base.where(col(WorkHour.employee_id).is_(None))  # type: ignore[arg-type,call-overload]
        return base


def _dept_col(model: Any, level: int) -> Any:
    mapping: dict[int, Any] = {
        1: model.level1_dept,
        2: model.level2_dept,
        3: model.level3_dept,
        4: model.level4_dept,
    }
    return mapping.get(level)


def _row_to_dict(row: Any, keys: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for i, key in enumerate(keys):
        try:
            result[key] = row[i]
        except (IndexError, TypeError):
            try:
                result[key] = getattr(row, key)
            except AttributeError:
                result[key] = None
    return result
