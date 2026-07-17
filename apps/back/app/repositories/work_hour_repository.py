"""工时仓储层(Repository / DAO): 封装工时数据的所有聚合查询。

持有 AsyncSession, 只做数据访问, 不包含业务逻辑。
"""

from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy import func, or_
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.employee import Employee
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
            return base.where(Employee.is_outsourced == 0)
        elif personnel_type == "外部人力资源":
            return base.where(or_(Employee.is_outsourced == 1, col(WorkHour.employee_id).is_(None)))  # type: ignore[arg-type]
        return base
