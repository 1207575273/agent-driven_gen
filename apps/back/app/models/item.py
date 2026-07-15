"""Item 实体 + 传输契约(SQLModel 全家桶)。

- ItemBase:   共享字段, 供各契约继承。
- Item:       表模型(table=True), 落库用。
- ItemCreate: 新增入参。
- ItemUpdate: 更新入参(全部可选)。
- ItemPublic: 出参, 显式暴露给前端的字段。

团队新增业务表照此在 app/models/ 下扩展, 并在 app/db/base.py 里 import 一次。
"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class ItemBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, index=True)
    description: str | None = Field(default=None, max_length=500)
    quantity: int = Field(default=0, ge=0)


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None


class ItemPublic(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
