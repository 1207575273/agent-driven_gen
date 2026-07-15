"""数据库引擎与会话(SQLite 异步 + WAL)。

get_session 作为请求级工作单元(Unit of Work): 请求成功自动 commit,
异常自动 rollback。Service 不各自 commit, 事务边界统一在此。
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    # SQL 回显由 core/logging.configure_logging 控制(避免 echo 额外挂 handler 造成双写)
    echo=False,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:  # pragma: no cover
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:  # pragma: no cover
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
