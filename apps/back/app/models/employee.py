"""Employee 实体与传输契约(SQLModel 全家桶模式)。

花名册数据: 人员信息、部门层级、角色、状态等。
"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class EmployeeBase(SQLModel):
    """公共业务字段基类: 不含 id 和审计时间戳。"""

    name: str = Field(min_length=1, max_length=50, index=True)
    employee_id: str | None = Field(default=None, max_length=50)
    position: str | None = Field(default=None, max_length=100)
    level1_dept: str | None = Field(default=None, max_length=100)
    level2_dept: str | None = Field(default=None, max_length=100, index=True)
    level3_dept: str | None = Field(default=None, max_length=100)
    level4_dept: str | None = Field(default=None, max_length=100)
    actual_team: str | None = Field(default=None, max_length=100)
    role: str | None = Field(default=None, max_length=50, index=True)
    employee_type: str | None = Field(default=None, max_length=50, index=True)
    employee_status: str | None = Field(default=None, max_length=50, index=True)
    position_name: str | None = Field(default=None, max_length=100)
    entry_date: date | None = None
    leave_date: date | None = None
    temp_report_note: str | None = Field(default=None, max_length=500)
    remarks: str | None = Field(default=None, max_length=500)
    is_outsourced: int = Field(default=0, index=True)
    match_status: str = Field(default="matched", max_length=20, index=True)


class Employee(EmployeeBase, table=True):
    """数据库表模型: 在 Base 之上补主键和审计时间戳。"""

    __tablename__ = "employees"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class EmployeeCreate(EmployeeBase):
    """新增入参: 直接复用 Base。"""


class EmployeeUpdate(SQLModel):
    """更新入参: 全部字段 Optional, 支持部分更新。"""

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
    position_name: str | None = None
    entry_date: date | None = None
    leave_date: date | None = None
    temp_report_note: str | None = None
    remarks: str | None = None
    is_outsourced: int | None = None
    match_status: str | None = None


class EmployeePublic(EmployeeBase):
    """出参契约: Base + id, 显式控制对外暴露字段。"""

    id: int
    created_at: datetime
    updated_at: datetime
