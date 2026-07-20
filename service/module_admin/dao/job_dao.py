"""定时任务数据访问操作。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.job_do import JobLogDo, ScheduledJobDo


class JobDao:
    """持久化定时任务和执行日志。"""

    @staticmethod
    async def list_jobs(request: Request, name: str | None, status: str | None, params: Params):
        """按名称和状态分页查询定时任务。"""
        query = select(ScheduledJobDo).order_by(ScheduledJobDo.id.desc())
        if name:
            query = query.where(ScheduledJobDo.job_name.contains(name))
        if status is not None:
            query = query.where(ScheduledJobDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def get_by_id(job_id: int, request: Request) -> ScheduledJobDo | None:
        """按编号查询定时任务。"""
        return await request.state.mysql.get(ScheduledJobDo, job_id)

    @staticmethod
    async def get_by_key(job_key: str, request: Request) -> ScheduledJobDo | None:
        """按任务标识查询定时任务。"""
        result = await request.state.mysql.execute(
            select(ScheduledJobDo).where(ScheduledJobDo.job_key == job_key)
        )
        return result.scalars().first()

    @staticmethod
    async def create(data, request: Request) -> ScheduledJobDo:
        """创建定时任务实体。"""
        item = ScheduledJobDo(
            **data.model_dump(),
            create_by=getattr(request.state, "user_id", None),
        )
        request.state.mysql.add(item)
        return item

    @staticmethod
    async def update(job_id: int, data, request: Request) -> ScheduledJobDo | None:
        """更新定时任务实体。"""
        item = await request.state.mysql.get(ScheduledJobDo, job_id)
        if item is None:
            return None
        item.sqlmodel_update(data.model_dump(exclude_unset=True))
        return item

    @staticmethod
    async def delete(job_id: int, request: Request) -> ScheduledJobDo | None:
        """删除定时任务实体。"""
        item = await request.state.mysql.get(ScheduledJobDo, job_id)
        if item is not None:
            await request.state.mysql.delete(item)
        return item

    @staticmethod
    async def list_logs(job_id: int, request: Request, params: Params):
        """分页查询定时任务执行日志。"""
        query = (
            select(JobLogDo)
            .where(JobLogDo.job_id == job_id)
            .order_by(JobLogDo.id.desc())
        )
        return await paginate(request.state.mysql, query, params=params)
