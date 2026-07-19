"""数据源抽象层: 隔离数据来源变化, 上层不感知文件格式。"""

from app.datasources.base import DataSourceProvider
from app.datasources.excel_provider import ExcelDataSourceProvider

__all__ = ["DataSourceProvider", "ExcelDataSourceProvider"]
