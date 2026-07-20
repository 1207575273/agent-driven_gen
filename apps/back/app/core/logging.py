"""生产级日志配置(structlog + stdlib logging 双出口)。

格式 / 滚动 / 留存由 config 的 logging 段**声明式控制**(见 core/config.LoggingSettings),
不写死在代码里 —— 改 APP_LOGGING__* 环境变量即可, 无需改码。

- 控制台:人类可读(带颜色, 非 TTY 自动关色), 供开发 / 运维直接看。
- 文件:**JSONL**, 字段固定且可预期:
    - `timestamp`  UTC ISO8601(带 Z);
    - `level`      日志级别;
    - `logger`     产生日志的 logger 名;
    - `message`    事件正文(聚合生态标准键, 由 structlog 的 event 重命名而来);
    - 其余为结构化上下文; 异常走 `exception` 结构化 traceback(非字符串)。
- 按配置的小时数滚动、保留配置的份数, 超出自动删除(过期自清)。

第三方(sqlalchemy / uvicorn)的 stdlib 日志经 foreign_pre_chain 归一到同一套字段与两个
出口。SQL 回显靠调 sqlalchemy.engine 的级别(不用引擎 echo, 避免额外 handler 双写)。
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog
from structlog.typing import EventDict, Processor, WrappedLogger

from app.core.config import LoggingSettings

# JSON 每行的标准字段固定前置, 其余上下文键随后, 保证形态可预期。
_FIELD_ORDER = ("timestamp", "level", "logger", "message")


def _order_fields(_: WrappedLogger, __: str, event_dict: EventDict) -> EventDict:
    ordered: dict[str, Any] = {}
    for key in _FIELD_ORDER:
        if key in event_dict:
            ordered[key] = event_dict.pop(key)
    ordered.update(event_dict)
    return ordered


def configure_logging(cfg: LoggingSettings) -> None:
    log_path = Path(cfg.dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 两个出口共用的前置处理器: 补 UTC 时间戳、级别、logger 名。
    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    # structlog 侧: 走完 shared 后交给 stdlib 的 ProcessorFormatter 按 handler 分别渲染。
    structlog.configure(
        processors=[*shared, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # 控制台: 人读(保留 event 为标题); 非 TTY 自动关闭 ANSI 颜色。
    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
            ],
        )
    )

    # 文件: JSONL, event->message, 结构化异常, 固定字段序, 按配置滚动 / 留存。
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_path / cfg.json_file,
        when=cfg.rotation_when,
        interval=cfg.rotation_interval_hours,
        backupCount=cfg.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.EventRenamer("message"),
                structlog.processors.dict_tracebacks,
                _order_fields,
                structlog.processors.JSONRenderer(ensure_ascii=False),
            ],
        )
    )

    root = logging.getLogger()
    # 幂等: 清掉已有 handler(含 basicConfig 默认), 避免重复配置导致多写。
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    root.setLevel(cfg.level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if cfg.sql_echo else logging.WARNING)
