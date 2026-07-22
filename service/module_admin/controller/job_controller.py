"""定时任务管理接口。"""

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.job_dto import (JobRunResultDto,
                                             ScheduledJobCreateDto,
                                             ScheduledJobDto,
                                             ScheduledJobUpdateDto)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.job_service import JobService


class JobController:
    """定时任务管理接口。"""

    job = APIRouter(prefix="/job", tags=["定时任务"])

    @job.get(
        "/list",
        summary="分页查询定时任务",
        dependencies=[Depends(Auth.has_permission("monitor:job:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[ScheduledJobDto]]}},
    )
    async def list_jobs(
        request: Request,
        name: str | None = Query(default=None, description="任务名称，支持模糊查询"),
        status: str | None = Query(
            default=None,
            pattern="^[01]$",
            description="任务状态：0停用，1正常",
        ),
        params: Params = Depends(),
    ):
        """分页查询已配置的定时任务。"""
        return await JobService.list_jobs(request, name, status, params)

    @job.post(
        "/add",
        summary="新增定时任务",
        dependencies=[Depends(Auth.has_permission("monitor:job:add"))],
        responses={200: {"model": ApiResponseDto[ScheduledJobDto]}},
    )
    async def create(data: ScheduledJobCreateDto, request: Request):
        """新增持久化定时任务。"""
        return await JobService.create(data, request)

    @job.get(
        "/{job_id}",
        summary="查询定时任务详情",
        dependencies=[Depends(Auth.has_permission("monitor:job:query"))],
        responses={200: {"model": ApiResponseDto[ScheduledJobDto]}},
    )
    async def detail(
        request: Request,
        job_id: int = Path(description="任务编号"),
    ):
        """查询定时任务详情。"""
        return await JobService.detail(job_id, request)

    @job.put(
        "/{job_id}",
        summary="修改定时任务",
        dependencies=[Depends(Auth.has_permission("monitor:job:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update(
        data: ScheduledJobUpdateDto,
        request: Request,
        job_id: int = Path(description="任务编号"),
    ):
        """修改定时任务配置。"""
        return await JobService.update(job_id, data, request)

    @job.delete(
        "/{job_id}",
        summary="删除定时任务",
        dependencies=[Depends(Auth.has_permission("monitor:job:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        job_id: int = Path(description="任务编号"),
    ):
        """删除定时任务。"""
        return await JobService.delete(job_id, request)

    @job.post(
        "/{job_id}/run",
        summary="立即执行定时任务",
        dependencies=[Depends(Auth.has_permission("monitor:job:run"))],
        responses={200: {"model": ApiResponseDto[JobRunResultDto]}},
    )
    async def run_now(
        request: Request,
        job_id: int = Path(description="任务编号"),
    ):
        """立即执行一次已注册处理器对应的任务。"""
        return await JobService.run_now(job_id, request)

    @job.get(
        "/{job_id}/log/list",
        summary="分页查询任务执行日志",
        dependencies=[Depends(Auth.has_permission("monitor:job:query"))],
        response_model=None,
    )
    async def logs(
        request: Request,
        job_id: int = Path(description="任务编号"),
        params: Params = Depends(),
    ):
        """分页查询指定任务的执行日志。"""
        return await JobService.list_logs(job_id, request, params)
