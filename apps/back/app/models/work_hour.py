"""WorkHour 实体与传输契约(SQLModel 全家桶模式)。

工时明细数据: 项目、填报人、投入人天等。
"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class WorkHourBase(SQLModel):
    """公共业务字段基类: 不含 id 和审计时间戳。"""

    project_name: str = Field(min_length=1, max_length=200, index=True)
    reporter: str = Field(min_length=1, max_length=50, index=True)
    reporter_department: str | None = Field(default=None, max_length=200)
    creator: str | None = Field(default=None, max_length=50)
    report_date: date
    hours: float = Field(default=0.0, ge=0)
    description: str | None = Field(default=None, max_length=2000)
    employee_id: int | None = Field(default=None, foreign_key="employees.id", index=True)


class WorkHour(WorkHourBase, table=True):
    """数据库表模型: 在 Base 之上补主键和审计时间戳。

    复合索引 (project_name, report_date) 通过 SQLModel __table_args__ 定义。
    """

    __tablename__ = "work_hours"
    __table_args__ = (
        # 复合索引: 按项目+日期快速聚合
        {"sqlite_autoincrement": True},
    )

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class WorkHourCreate(WorkHourBase):
    """新增入参: 直接复用 Base。"""


class WorkHourUpdate(SQLModel):
    """更新入参: 全部字段 Optional, 支持部分更新。"""

    project_name: str | None = None
    reporter: str | None = None
    reporter_department: str | None = None
    creator: str | None = None
    report_date: date | None = None
    hours: float | None = None
    description: str | None = None
    employee_id: int | None = None


class WorkHourPublic(WorkHourBase):
    """出参契约: Base + id。"""

    id: int
    created_at: datetime
