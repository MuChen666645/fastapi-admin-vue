"""注册任务与 APScheduler 的持久化调度集成。"""

import inspect
import json
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from sqlmodel import select

from module_admin.entity.do.job_do import JobLogDo, ScheduledJobDo
from utils.time_utils import now_utc8_naive


TaskHandler = Callable[[dict[str, Any]], Any | Awaitable[Any]]


class JobScheduler:
    """调度数据库中已持久化且由代码注册处理器的任务。"""

    JOB_PREFIX = "scheduled-job:"

    def __init__(self, session_factory_provider, timezone: str) -> None:
        self._session_factory_provider = session_factory_provider
        self._scheduler = AsyncIOScheduler(timezone=timezone)
        self._handlers: dict[str, TaskHandler] = {}
        self._started = False

    def register_task(self, task_name: str, handler: TaskHandler) -> None:
        """按名称注册进程内任务处理器。"""
        self._handlers[task_name] = handler

    async def start(self) -> None:
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
        session_factory = self._session_factory_provider()
        if session_factory is None:
            return "failed", "数据库会话未初始化"

        async with session_factory() as session:
            job = await session.get(ScheduledJobDo, job_id)
            if job is None:
                return "failed", "定时任务不存在"
            handler = self._handlers.get(job.task_name)
            if handler is None:
                message = f"任务处理器未注册：{job.task_name}"
                await self._save_result(session, job, "failed", message)
                return "failed", message
            try:
                args = json.loads(job.args_json or "{}")
                if not isinstance(args, dict):
                    raise ValueError("任务参数必须是 JSON 对象")
                result = handler(args)
                if inspect.isawaitable(result):
                    result = await result
                message = None if result is None else str(result)[:2000]
                await self._save_result(session, job, "success", message)
                return "success", message
            except Exception as exc:
                message = str(exc)[:2000]
                logger.exception("定时任务执行失败", job_id=job_id)
                await self._save_result(session, job, "failed", message)
                return "failed", message

    @staticmethod
    async def _save_result(
        session,
        job: ScheduledJobDo,
        status: str,
        message: str | None,
    ) -> None:
        """更新任务最近一次状态并写入执行日志。"""
        now = now_utc8_naive()
        job.last_run_time = now
        job.last_status = status
        job.last_message = message
        session.add(
            JobLogDo(
                job_id=job.id,
                task_name=job.task_name,
                status=status,
                message=message,
                start_time=now,
                end_time=now,
                duration_ms=0,
            )
        )
        await session.commit()
