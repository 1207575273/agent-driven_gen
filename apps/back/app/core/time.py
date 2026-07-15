"""时间工具: 统一使用带时区的 UTC, 避免 naive datetime 混用。"""

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)
