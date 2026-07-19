"""ShouldBeCapacity 应有产能实体。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ShouldBeCapacityBase(SQLModel):
    """应有产能公共字段。"""

    employee_id: int = Field(foreign_key="employees.id", index=True)
    year_month: str = Field(max_length=7, index=True)  # "2026-01"
    total_working_days: int = Field(default=0, ge=0)
    active_working_days: int = Field(default=0, ge=0)
    capacity_days: float = Field(default=0.0, ge=0)


class ShouldBeCapacity(ShouldBeCapacityBase, table=True):
    __tablename__ = "should_be_capacity"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class ShouldBeCapacityCreate(ShouldBeCapacityBase):
    """新增入参: 复用 Base 字段。"""


class ShouldBeCapacityUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    employee_id: int | None = None
    year_month: str | None = None
    total_working_days: int | None = None
    active_working_days: int | None = None
    capacity_days: float | None = None


class ShouldBeCapacityPublic(ShouldBeCapacityBase):
    """出参: 暴露 id 与审计时间戳。"""

    id: int
    created_at: datetime
