"""产能分析系统的共享数据类。

QueryFilters: 所有聚合查询方法接受的通用筛选参数。
"""

from dataclasses import dataclass
from datetime import date


@dataclass
class QueryFilters:
    """通用筛选条件。

    所有聚合查询方法接受同一组 filters 参数, 逐层透传。
    """

    start_date: date | None = None
    end_date: date | None = None
    department: str | None = None
    department_level: int = 2
    role: str | None = None
    personnel_type: str | None = None
    project_name: str | None = None
