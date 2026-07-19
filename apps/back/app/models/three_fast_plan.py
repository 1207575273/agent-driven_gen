"""ThreeFastPlan 三快产能计划实体。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ThreeFastPlanBase(SQLModel):
    """三快计划公共字段。"""

    plan_quarter: str = Field(max_length=10)  # "2026-Q1" / "2026-Q2"
    category_id: int = Field(foreign_key="project_categories.id", index=True)
    plan_days: float = Field(default=0.0, ge=0)


class ThreeFastPlan(ThreeFastPlanBase, table=True):
    __tablename__ = "three_fast_plans"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class ThreeFastPlanCreate(ThreeFastPlanBase):
    """新增入参: 复用 Base 字段。"""


class ThreeFastPlanUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    plan_quarter: str | None = None
    category_id: int | None = None
    plan_days: float | None = None


class ThreeFastPlanPublic(ThreeFastPlanBase):
    """出参: 暴露 id 与审计时间戳。"""

    id: int
    created_at: datetime
