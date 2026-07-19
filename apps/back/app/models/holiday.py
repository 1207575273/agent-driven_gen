"""Holiday 节假日实体。"""

from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.core.time import utcnow


class HolidayBase(SQLModel):
    """节假日公共字段。"""

    holiday_name: str = Field(max_length=100)
    holiday_date: date = Field(index=True)
    is_workday: bool = Field(default=False)


class Holiday(HolidayBase, table=True):
    __tablename__ = "holidays"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow)


class HolidayCreate(HolidayBase):
    """新增入参: 复用 Base 字段。"""


class HolidayUpdate(SQLModel):
    """更新入参: 全字段可选。"""

    holiday_name: str | None = None
    holiday_date: date | None = None
    is_workday: bool | None = None


class HolidayPublic(HolidayBase):
    """出参: 暴露 id 与审计时间戳。"""

    id: int
    created_at: datetime
