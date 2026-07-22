"""注册任务与 APScheduler 的持久化调度集成。"""

import inspect
import json
import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from sqlmodel import select

from module_admin.entity.do.job_do import JobLogDo, ScheduledJobDo
from module_admin.service.alert_service import AlertService
from utils.time_utils import now_utc8_naive


TaskHandler = Callable[[dict[str, Any]], Any | Awaitable[Any]]


class JobScheduler:
    """调度数据库中已持久化且由代码注册处理器的任务。"""

    # APScheduler 任务 ID 使用此前缀，便于清理本应用管理的任务。
    JOB_PREFIX = "scheduled-job:"

    def __init__(
        self,
        session_factory_provider,
        timezone: str,
        redis=None,
        default_timeout: int = 300,
        lock_ttl: int = 900,
        default_max_retries: int = 0,
        metrics=None,
        alert_webhook_url: str = "",
    ) -> None:
        """创建延迟解析当前数据库会话工厂的调度器。"""
        self._session_factory_provider = session_factory_provider
        self._scheduler = AsyncIOScheduler(timezone=timezone)
        self._handlers: dict[str, TaskHandler] = {}
        self._started = False
        self._redis = redis
        self._default_timeout = default_timeout
        self._lock_ttl = lock_ttl
        self._default_max_retries = default_max_retries
        self._instance_id = uuid.uuid4().hex
        self._metrics = metrics
        self._alert_webhook_url = alert_webhook_url

    def register_task(self, task_name: str, handler: TaskHandler) -> None:
        """按名称注册进程内任务处理器。"""
        self._handlers[task_name] = handler

    async def start(self) -> None:
        """启动调度器，并立即同步数据库中的持久化任务。"""
        if self._started:
            return
        self._scheduler.start()
        self._scheduler.add_job(
            self.refresh,
            "interval",
            seconds=30,
            id="scheduled-job-refresh",
            replace_existing=True,
        )
        self._started = True
        await self.refresh()

    async def stop(self) -> None:
        """停止后续调度，不等待已经运行的任务。"""
        if not self._started:
            return
        self._scheduler.shutdown(wait=False)
        self._started = False

    async def refresh(self) -> None:
        """同步数据库启用任务与已注册的任务处理器。"""
        session_factory = self._session_factory_provider()
        if session_factory is None:
            return
        async with session_factory() as session:
            result = await session.execute(
                select(ScheduledJobDo).where(ScheduledJobDo.status == "1")
            )
            jobs = list(result.scalars().all())

        enabled_ids = {job.id for job in jobs}
        for scheduled_job in list(self._scheduler.get_jobs()):
            if scheduled_job.id.startswith(self.JOB_PREFIX):
                job_id = int(scheduled_job.id.removeprefix(self.JOB_PREFIX))
                if job_id not in enabled_ids:
                    scheduled_job.remove()

        for job in jobs:
            if job.id is None or job.task_name not in self._handlers:
                continue
            try:
                trigger = CronTrigger.from_crontab(job.cron_expression)
                self._scheduler.add_job(
                    self._execute,
                    trigger=trigger,
                    id=f"{self.JOB_PREFIX}{job.id}",
                    replace_existing=True,
                    kwargs={"job_id": job.id},
                )
            except ValueError:
                logger.error("定时任务的 Cron 表达式无效", job_id=job.id)

    async def run_now(self, job_id: int) -> tuple[str, str | None]:
        """立即执行一次启用的定时任务。"""
        return await self._execute(job_id=job_id)

    async def _execute(self, job_id: int) -> tuple[str, str | None]:
        """执行任务并保存执行结果。"""
        lock_key = f"scheduled-job:lock:{job_id}"
        if self._redis is not None:
            try:
                acquired = await self._redis.set(
                    lock_key,
                    self._instance_id,
                    ex=self._lock_ttl,
                    nx=True,
                )
            except TypeError:
                acquired = True
            if not acquired:
                return "skipped", "任务正在其他实例执行"
        session_factory = self._session_factory_provider()
        if session_factory is None:
            await self._release_lock(lock_key)
            return "failed", "数据库会话未初始化"
        started_at = time.perf_counter()
        try:
            async with session_factory() as session:
                job = await session.get(ScheduledJobDo, job_id)
                if job is None:
                    return "failed", "定时任务不存在"
                handler = self._handlers.get(job.task_name)
                if handler is None:
                    message = f"任务处理器未注册：{job.task_name}"
                    await self._save_result(session, job, "failed", message, started_at, self._metrics)
                    await AlertService.notify_job_failure(
                        self._alert_webhook_url,
                        job.id,
                        job.task_name,
                        message,
                        self._metrics,
                    )
                    return "failed", message
                try:
                    args = json.loads(job.args_json or "{}")
                    if not isinstance(args, dict):
                        raise ValueError("任务参数必须是 JSON 对象")
                    retries = max(job.max_retries, self._default_max_retries)
                    timeout = job.timeout_seconds or self._default_timeout
                    for attempt in range(retries + 1):
                        try:
                            if inspect.iscoroutinefunction(handler):
                                result = await asyncio.wait_for(
                                    handler(args), timeout=timeout
                                )
                            else:
                                result = await asyncio.wait_for(
                                    asyncio.to_thread(handler, args),
                                    timeout=timeout,
                                )
                            message = None if result is None else str(result)[:2000]
                            await self._save_result(session, job, "success", message, started_at, self._metrics)
                            return "success", message
                        except Exception as exc:
                            if attempt >= retries:
                                raise
                            logger.warning(
                                "定时任务执行失败，将重试",
                                job_id=job_id,
                                attempt=attempt + 1,
                            )
                    raise RuntimeError("任务未执行")
                except Exception as exc:
                    message = str(exc)[:2000]
                    await AlertService.notify_job_failure(
                        self._alert_webhook_url,
                        job.id,
                        job.task_name,
                        message,
                        self._metrics,
                    )
                    logger.exception("定时任务执行失败", job_id=job_id)
                    await self._save_result(session, job, "failed", message, started_at, self._metrics)
                    return "failed", message
        finally:
            await self._release_lock(lock_key)

    async def _release_lock(self, lock_key: str) -> None:
        """释放当前实例持有的任务锁。"""
        if self._redis is not None:
            await self._redis.delete(lock_key)

    @staticmethod
    async def _save_result(
        session,
        job: ScheduledJobDo,
        status: str,
        message: str | None,
        started_at: float | None = None,
        metrics=None,
    ) -> None:
        """更新任务最近一次状态并写入执行日志。"""
        now = now_utc8_naive()
        job.last_run_time = now
        job.last_status = status
        job.last_message = message
        session.add(
            JobLogDo(
                job_id=job.id,
                tenant_id=job.tenant_id,
                task_name=job.task_name,
                status=status,
                message=message,
                start_time=now,
                end_time=now,
                duration_ms=0,
            )
        )
        await session.commit()
        if metrics is not None:
            metrics.job_executions.labels(str(job.id), status).inc()
            if started_at is not None:
                metrics.job_duration.labels(str(job.id)).observe(
                    time.perf_counter() - started_at
                )
