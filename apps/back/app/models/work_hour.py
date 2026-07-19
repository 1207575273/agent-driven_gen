"""WorkHour 工时明细实体与传输契约(SQLModel 全家桶)。"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class WorkHourBase(SQLModel):
    """工时明细公共字段。"""

    project_name: str = Field(max_length=500, index=True)
    reporter: str = Field(max_length=200)
    reporter_department: str | None = Field(default=None, max_length=200)
    creator: str | None = Field(default=None, max_length=200)
    report_date: date = Field(index=True)
    hours: float = Field(default=0.0, ge=0)
    description: str | None = Field(default=None, max_length=2000)
    employee_id: int | None = Field(default=None, foreign_key="employees.id", index=True)
    matched_project_name: str | None = Field(default=None, max_length=500, index=True)
    category_id: int | None = Field(default=None, foreign_key="project_categories.id", index=True)


class WorkHour(WorkHourBase, table=True):
    __tablename__ = "work_hours"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class WorkHourCreate(WorkHourBase):
    """新增入参: 复用 Base 字段。"""


class WorkHourUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    project_name: str | None = None
    reporter: str | None = None
    reporter_department: str | None = None
    creator: str | None = None
    report_date: date | None = None
    hours: float | None = None
    description: str | None = None
    employee_id: int | None = None
    matched_project_name: str | None = None
    category_id: int | None = None


class WorkHourPublic(WorkHourBase):
    """出参: 暴露 id 与创建时间戳。"""

    id: int
    created_at: datetime
