"""定时任务管理业务服务。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params
from apscheduler.triggers.cron import CronTrigger

from module_admin.dao.job_dao import JobDao


class JobService:
    """校验定时任务并协调运行时调度器。"""

    @staticmethod
    def _validate_cron(expression: str) -> None:
        """校验五段式 Cron 表达式。"""
        try:
            CronTrigger.from_crontab(expression)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Cron 表达式无效") from exc

    @staticmethod
    async def list_jobs(request: Request, name, status, params: Params):
        """分页查询定时任务。"""
        return await JobDao.list_jobs(request, name, status, params)

    @staticmethod
    async def detail(job_id: int, request: Request):
        """查询定时任务详情。"""
        item = await JobDao.get_by_id(job_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="定时任务不存在")
        return item

    @staticmethod
    async def create(data, request: Request):
        """创建定时任务并校验任务标识唯一性。"""
        JobService._validate_cron(data.cron_expression)
        if await JobDao.get_by_key(data.job_key, request):
            raise HTTPException(status_code=409, detail="任务标识已存在")
        return await JobDao.create(data, request)

    @staticmethod
    async def update(job_id: int, data, request: Request):
        """更新定时任务。"""
        if data.cron_expression:
            JobService._validate_cron(data.cron_expression)
        if await JobDao.update(job_id, data, request) is None:
            raise HTTPException(status_code=404, detail="定时任务不存在")

    @staticmethod
    async def delete(job_id: int, request: Request):
        """删除定时任务。"""
        if await JobDao.delete(job_id, request) is None:
            raise HTTPException(status_code=404, detail="定时任务不存在")

    @staticmethod
    async def run_now(job_id: int, request: Request):
        """立即执行一次定时任务。"""
        await JobService.detail(job_id, request)
        scheduler = getattr(request.app.state, "scheduler", None)
        if scheduler is None:
            raise HTTPException(status_code=503, detail="定时任务调度器未启用")
        status, message = await scheduler.run_now(job_id)
        return {"job_id": job_id, "status": status, "message": message}

    @staticmethod
    async def list_logs(job_id: int, request: Request, params: Params):
        """分页查询定时任务执行日志。"""
        await JobService.detail(job_id, request)
        return await JobDao.list_logs(job_id, request, params)
