"""进程内定时任务(APScheduler AsyncIOScheduler)。

与母版"单进程同源"一致: 不另起 worker / 系统 cron, 随 FastAPI lifespan 起停,
复用同一个事件循环。

重要约束:
- **多实例会重复触发**: in-process 调度在每个进程 / worker 各跑一份。母版是单
  worker(start.mjs 未开 --workers), 当前无碍; 上多副本时需换持久 jobstore + 分布式锁,
  或改用外部调度器(系统 cron / K8s CronJob 打内部 GET)。母版不预置(YAGNI)。
- **job 在请求作用域外**: 拿不到 Depends(get_session), 但仍禁止在 job 内直接写 SQL ——
  一律 session_scope() 自建会话 + 经 service, 守住三层。
"""

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.session import session_scope
from app.repositories.item_repository import ItemRepository
from app.services.item_service import ItemService

logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def log_item_count() -> None:
    """示例 job: 周期性记录当前 Item 总数(经 service.count, 不碰 SQL)。"""
    async with session_scope() as session:
        service = ItemService(ItemRepository(session))
        total = await service.count()
    logger.info("scheduled.item_count", total=total)


def register_jobs() -> None:
    """注册所有定时任务。团队新增 job 在此 add_job 即可。"""
    scheduler.add_job(
        log_item_count,
        trigger="interval",
        seconds=60,
        id="log_item_count",
        replace_existing=True,
        max_instances=1,  # 上一轮没跑完就跳过本轮, 避免堆叠
        coalesce=True,  # 错过多次只补跑一次
    )
