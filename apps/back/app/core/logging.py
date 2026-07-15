"""日志基线配置。

母版默认打印每条 SQL(sql_echo=True), 便于开发期排查;
生产可用 APP_SQL_ECHO=false 关闭 SQL 回显, APP_LOG_LEVEL=WARNING 降噪。

SQL 回显不用引擎 echo(那会额外挂一个 handler 导致日志双写),
而是把 sqlalchemy.engine 日志级别设为 INFO, 走统一的 root handler 打印一份。
"""

import logging


def configure_logging(level: str = "INFO", *, sql_echo: bool = True) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if sql_echo else logging.WARNING)
