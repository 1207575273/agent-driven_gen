"""Employee 花名册实体与传输契约(SQLModel 全家桶)。"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class EmployeeBase(SQLModel):
    """花名册公共字段。"""

    name: str = Field(max_length=100, index=True)
    employee_id: str | None = Field(default=None, max_length=50, index=True)
    position: str | None = Field(default=None, max_length=200)
    level1_dept: str | None = Field(default=None, max_length=200)
    level2_dept: str | None = Field(default=None, max_length=200, index=True)
    level3_dept: str | None = Field(default=None, max_length=200)
    level4_dept: str | None = Field(default=None, max_length=200)
    actual_team: str | None = Field(default=None, max_length=200)
    role: str | None = Field(default=None, max_length=200)
    employee_type: str | None = Field(default=None, max_length=100)
    employee_status: str | None = Field(default=None, max_length=50, index=True)
    position_type: str | None = Field(default=None, max_length=100)
    entry_date: date | None = Field(default=None)
    leave_date: date | None = Field(default=None)
    fill_note: str | None = Field(default=None, max_length=500)
    remarks: str | None = Field(default=None, max_length=1000)
    planned_project1: str | None = Field(default=None, max_length=500)
    planned_project2: str | None = Field(default=None, max_length=500)
    planned_project3: str | None = Field(default=None, max_length=500)
    planned_project4: str | None = Field(default=None, max_length=500)
    planned_project5: str | None = Field(default=None, max_length=500)
    is_excluded: bool = Field(default=False, index=True)


class Employee(EmployeeBase, table=True):
    __tablename__ = "employees"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class EmployeeCreate(EmployeeBase):
    """新增入参: 复用 Base 字段。"""


class EmployeeUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    name: str | None = None
    employee_id: str | None = None
    position: str | None = None
    level1_dept: str | None = None
    level2_dept: str | None = None
    level3_dept: str | None = None
    level4_dept: str | None = None
    actual_team: str | None = None
    role: str | None = None
    employee_type: str | None = None
    employee_status: str | None = None
    position_type: str | None = None
    entry_date: date | None = None
    leave_date: date | None = None
    fill_note: str | None = None
    remarks: str | None = None
    planned_project1: str | None = None
    planned_project2: str | None = None
    planned_project3: str | None = None
    planned_project4: str | None = None
    planned_project5: str | None = None
    is_excluded: bool | None = None


class EmployeePublic(EmployeeBase):
    """出参: 暴露 id 与审计时间戳。"""

    id: int
    created_at: datetime
    updated_at: datetime
