"""ProjectCategory 项目分类(自引用树形表) + 三快计划实体。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ProjectCategoryBase(SQLModel):
    """项目分类公共字段。"""

    category_name: str = Field(max_length=200)
    category_level: int = Field(ge=1, le=3)
    sort_order: int = Field(default=0)
    parent_id: int | None = Field(default=None, foreign_key="project_categories.id")


class ProjectCategory(ProjectCategoryBase, table=True):
    __tablename__ = "project_categories"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class ProjectCategoryCreate(ProjectCategoryBase):
    """新增入参: 复用 Base 字段。"""


class ProjectCategoryUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    category_name: str | None = None
    category_level: int | None = None
    sort_order: int | None = None
    parent_id: int | None = None


class ProjectCategoryPublic(ProjectCategoryBase):
    """出参: 暴露 id 与审计时间戳。"""

    id: int
    created_at: datetime
