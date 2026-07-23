"""独立可靠任务 Worker 进程入口。"""

import asyncio
import signal
from contextlib import suppress
from types import SimpleNamespace

from loguru import logger

from config.env import settings
from config.mysql_serve import MysqlServe
from config.redis_serve import RedisServe
from module_admin.service.job_worker import JobWorker


async def run() -> None:
    """建立独立依赖并运行 Worker。"""
    if not settings.WORKER_ENABLED:
        logger.info("Worker is disabled by WORKER_ENABLED")
        return
    redis = await RedisServe.get_redis_server(settings)
    engine, session_factory = await MysqlServe.get_mysql_config(settings)
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signal_name in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(signal_name, stop_event.set)
    worker = JobWorker(session_factory, redis, settings)
    try:
        await worker.run(stop_event)
    finally:
        await worker.close()
        await engine.dispose()
        await RedisServe.close_redis_server(
            SimpleNamespace(state=SimpleNamespace(redis=redis))
        )


if __name__ == "__main__":
    asyncio.run(run())
