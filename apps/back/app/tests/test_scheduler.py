"""定时任务测试: 直接 await job, 用测试会话替换 session_scope 隔离数据库。"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import scheduler as scheduler_mod
from app.models.item import Item


async def test_should_run_log_item_count_via_service(session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> None:
    session.add(Item(name="x", quantity=3))
    await session.flush()

    @asynccontextmanager
    async def fake_scope() -> AsyncGenerator[AsyncSession, None]:
        yield session

    # job 内部用的是 scheduler 模块里绑定的 session_scope, 替换成测试会话
    monkeypatch.setattr(scheduler_mod, "session_scope", fake_scope)

    # 经 service.count 读取, 不抛异常即通过
    await scheduler_mod.log_item_count()


def test_should_register_demo_job() -> None:
    scheduler_mod.register_jobs()

    job_ids = [job.id for job in scheduler_mod.scheduler.get_jobs()]
    assert "log_item_count" in job_ids
