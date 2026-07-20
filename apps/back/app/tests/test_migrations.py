"""迁移冒烟: 确认 Alembic upgrade head 能把空库建到位(替代原 create_all 路径)。

顺带守住"启动即迁移"这条链: 初始迁移或 env.py 出问题时这里会红。
"""

import sqlite3
from pathlib import Path

import pytest

from app.core.config import settings
from app.db.migrate import run_migrations_to_head


def _table_names(db_path: Path) -> set[str]:
    con = sqlite3.connect(db_path)
    try:
        rows = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    finally:
        con.close()
    return {row[0] for row in rows}


def test_should_create_item_table_when_migrating_empty_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "migrate.db"
    monkeypatch.setattr(settings, "database_url", f"sqlite+aiosqlite:///{db_path.as_posix()}")

    run_migrations_to_head()

    tables = _table_names(db_path)
    assert "item" in tables  # 业务表建出来了
    assert "alembic_version" in tables  # 走的是迁移路径, 有版本记录(区别于 create_all)
