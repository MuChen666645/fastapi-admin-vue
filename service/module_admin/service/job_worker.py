"""独立任务 Worker。"""

import asyncio
import importlib
from contextlib import suppress

from loguru import logger

from config.env import Settings, settings
from module_admin.service.job_scheduler import JobScheduler, TaskHandler
from module_admin.service.task_queue import TaskQueue


def load_task_handlers(
    module_name: str = "module_admin.service.task_handlers",
) -> dict[str, TaskHandler]:
    """从配置模块加载 Worker 任务处理器。"""
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return {}
    handlers = getattr(module, "HANDLERS", {})
    return dict(handlers) if isinstance(handlers, dict) else {}


class JobWorker:
    """消费可靠任务队列并复用统一任务执行和锁续租逻辑。"""

    def __init__(self, session_factory, redis, app_settings: Settings | None = None):
        self.settings = app_settings or settings
        self.queue = TaskQueue(
            redis,
            self.settings.TASK_QUEUE_STREAM,
            self.settings.TASK_QUEUE_GROUP,
        )
        self.scheduler = JobScheduler(
            lambda: session_factory,
            timezone=self.settings.SCHEDULER_TIMEZONE,
            redis=redis,
            default_timeout=self.settings.SCHEDULER_DEFAULT_TIMEOUT_SECONDS,
            lock_ttl=self.settings.SCHEDULER_LOCK_TTL_SECONDS,
            default_max_retries=self.settings.SCHEDULER_DEFAULT_MAX_RETRIES,
            worker_mode="inline",
            lock_renew_seconds=self.settings.TASK_LOCK_RENEW_SECONDS,
        )
        for task_name, handler in load_task_handlers(
            self.settings.TASK_HANDLER_MODULE
        ).items():
            self.scheduler.register_task(task_name, handler)
        self._consumer: str | None = None

    async def _heartbeat_loop(self, consumer: str) -> None:
        """持续刷新 Worker 存活标记，避免长任务期间被误判为失联。"""
        interval = self.settings.TASK_HEARTBEAT_SECONDS
        while True:
            try:
                await self.queue.heartbeat(consumer, interval)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Worker 心跳刷新失败", consumer=consumer)
            await asyncio.sleep(interval)

    async def run(self, stop_event: asyncio.Event | None = None) -> None:
        """持续消费，直到收到停止信号。"""
        await self.queue.ensure_group()
        stop_event = stop_event or asyncio.Event()
        consumer = self.settings.TASK_WORKER_CONSUMER or self.scheduler._instance_id
        self._consumer = consumer
        heartbeat_task = asyncio.create_task(self._heartbeat_loop(consumer))
        try:
            while not stop_event.is_set():
                message = await self.queue.read(consumer)
                if message is None:
                    continue
                try:
                    await self.scheduler._execute(message.job_id)
                except Exception:
                    logger.exception("可靠任务消息执行失败", job_id=message.job_id)
                    continue
                else:
                    await self.queue.ack(message.message_id)
        finally:
            heartbeat_task.cancel()
            with suppress(asyncio.CancelledError):
                await heartbeat_task
            await self.queue.clear_heartbeat(consumer)

    async def close(self) -> None:
        """停止 Worker 内部调度器。"""
        if self._consumer is not None:
            await self.queue.clear_heartbeat(self._consumer)
        await self.scheduler.stop()
