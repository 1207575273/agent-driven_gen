"""数据源抽象基类(ABC): 定义 5 个抽象方法, 各数据源实现自己的读取逻辑。"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class ImportContext:
    """导入上下文: 承载导入统计与错误收集。"""

    stats: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class DataSourceProvider(ABC):
    """数据源抽象提供者。每个数据源实现自己的读取逻辑。"""

    @abstractmethod
    def provide_employees(self) -> Iterator[dict[str, object]]:
        """逐行输出花名册记录(dict)。"""
        ...

    @abstractmethod
    def provide_work_hours(self) -> Iterator[dict[str, object]]:
        """逐行输出工时明细记录(dict)。"""
        ...

    @abstractmethod
    def provide_project_categories(self) -> list[dict[str, object]]:
        """输出项目分类配置(list, 数据量小可一次性返回)。"""
        ...

    @abstractmethod
    def provide_holidays(self) -> list[dict[str, object]]:
        """输出节假日日历。"""
        ...

    @abstractmethod
    def provide_three_fast_plans(self) -> list[dict[str, object]]:
        """输出三快计划分配(可选, 无数据返回空列表)。"""
        ...
