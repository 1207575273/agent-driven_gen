"""启动时迁移: 统一走 Alembic upgrade head, 不再用 create_all。

为什么不用 create_all: create_all 只建"缺失的表", 不会 alter 已存在的表。
团队后续用 Alembic 加字段时, 若还留着 create_all, 会误以为迁移生效而实际漏迁移
(默认即错)。因此母版启动就走迁移路径, 让开发/生产与迁移历史始终一致。

实现要点: Alembic 的 env.py 在 online 模式里自行 `asyncio.run(...)`。若在 FastAPI
lifespan(已有运行中的事件循环)里直接调 command.upgrade, 会触发"asyncio.run 不能嵌套"。
因此 lifespan 用 `asyncio.to_thread(run_migrations_to_head)` 放到独立线程执行
(该线程无运行中的 loop, env.py 的 asyncio.run 可正常工作)。
"""

from pathlib import Path

from alembic import command
from alembic.config import Config

_BACK_DIR = Path(__file__).resolve().parent.parent.parent  # apps/back


def _alembic_config() -> Config:
    """构造指向本项目 alembic.ini / migrations 的绝对路径配置(不依赖调用时的 CWD)。"""
    cfg = Config(str(_BACK_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACK_DIR / "migrations"))
    return cfg


def run_migrations_to_head() -> None:
    """把数据库迁移到最新版本(head)。启动时经 asyncio.to_thread 调用, 见模块 docstring。"""
    command.upgrade(_alembic_config(), "head")
