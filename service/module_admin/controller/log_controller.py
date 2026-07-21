"""系统日志和在线会话管理接口。"""

from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request, Query
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.log_dto import (
    BatchLogIdsDto,
    ExceptionLogDto,
    ForceLogoutUserResultDto,
    LoginLogDto,
    LogQueryDto,
    OnlineQueryDto,
    OnlineSessionDto,
    OperationLogDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.log_service import LogService


class LogController:
    """提供登录、操作、异常日志和在线会话管理接口。"""

    log = APIRouter(prefix="/log", tags=["日志管理"])
    online = APIRouter(prefix="/online", tags=["在线用户管理"])

    @staticmethod
    async def _list(log_type: str, query: LogQueryDto, params: Params, request: Request):
        """将带类型的日志查询委托给日志服务。"""
        return await LogService.list_logs(log_type, query, params, request)

    @staticmethod
    def _build_log_query(
        username: str | None,
        status: str | None,
        path: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> LogQueryDto:
        """构造所有日志列表接口共用的过滤条件 DTO。"""
        return LogQueryDto(
            username=username,
            status=status,
            path=path,
            start_time=start_time,
            end_time=end_time,
        )

    @log.get(
        "/login/list",
        summary="登录日志列表",
        dependencies=[Depends(Auth.has_permission("monitor:login:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[LoginLogDto]]}},
    )
    async def login_logs(
        request: Request,
        username: str | None = Query(
            default=None, description="用户名，支持模糊查询"
        ),
        status: str | None = Query(
            default=None, pattern="^[01]$", description="登录状态：0失败，1成功"
        ),
        path: str | None = Query(default=None, description="请求路径，支持模糊查询"),
        start_time: datetime | None = Query(default=None, description="查询开始时间"),
        end_time: datetime | None = Query(default=None, description="查询结束时间"),
        params: Params = Depends(),
    ):
        """分页查询登录日志。"""
        query = LogController._build_log_query(
            username, status, path, start_time, end_time
        )
        return await LogController._list("login", query, params, request)

    @log.get(
        "/operation/list",
        summary="操作日志列表",
        dependencies=[Depends(Auth.has_permission("monitor:operation:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[OperationLogDto]]}},
    )
    async def operation_logs(
        request: Request,
        username: str | None = Query(
            default=None, description="用户名，支持模糊查询"
        ),
        status: str | None = Query(
            default=None, pattern="^[01]$", description="登录状态：0失败，1成功"
        ),
        path: str | None = Query(default=None, description="请求路径，支持模糊查询"),
        start_time: datetime | None = Query(default=None, description="查询开始时间"),
        end_time: datetime | None = Query(default=None, description="查询结束时间"),
        params: Params = Depends(),
    ):
        """分页查询操作日志。"""
        query = LogController._build_log_query(
            username, status, path, start_time, end_time
        )
        return await LogController._list("operation", query, params, request)

    @log.get(
        "/exception/list",
        summary="异常日志列表",
        dependencies=[Depends(Auth.has_permission("monitor:exception:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[ExceptionLogDto]]}},
    )
    async def exception_logs(
        request: Request,
        username: str | None = Query(
            default=None, description="用户名，支持模糊查询"
        ),
        status: str | None = Query(
            default=None, pattern="^[01]$", description="登录状态：0失败，1成功"
        ),
        path: str | None = Query(default=None, description="请求路径，支持模糊查询"),
        start_time: datetime | None = Query(default=None, description="查询开始时间"),
        end_time: datetime | None = Query(default=None, description="查询结束时间"),
        params: Params = Depends(),
    ):
        """分页查询异常日志。"""
        query = LogController._build_log_query(
            username, status, path, start_time, end_time
        )
        return await LogController._list("exception", query, params, request)

    @log.delete(
        "/{log_type}/batch",
        summary="批量删除日志",
        dependencies=[Depends(Auth.has_permission("monitor:log:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_logs(
        request: Request,
        data: BatchLogIdsDto = Body(
            title="批量删除日志请求",
            description="批量删除登录日志、操作日志或异常日志的请求参数",
        ),
        log_type: str = Path(
            pattern="^(login|operation|exception)$",
            description="日志类型：login登录日志、operation操作日志、exception异常日志",
        ),
    ):
        """按日志类型批量删除日志。"""
        await LogService.delete_logs(log_type, data.ids, request)

    @online.get(
        "/list",
        summary="在线用户列表",
        dependencies=[Depends(Auth.has_permission("monitor:online:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[OnlineSessionDto]]}},
    )
    async def online_users(
        request: Request,
        username: str | None = Query(
            default=None, description="用户名，支持模糊查询"
        ),
        ip_address: str | None = Query(
            default=None, description="登录IP，支持模糊查询"
        ),
        params: Params = Depends(),
    ):
        """分页查询当前数据权限范围内的在线会话。"""
        query = OnlineQueryDto(username=username, ip_address=ip_address)
        return await LogService.list_online_users(query, params, request)

    @online.delete(
        "/token/{token_id}",
        summary="强制指定 Token 下线",
        dependencies=[Depends(Auth.has_permission("monitor:online:forceLogout"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def revoke_token(
        request: Request,
        token_id: str = Path(
            min_length=64, max_length=64, description="Token会话ID"
        ),
    ):
        """强制指定 Token 会话下线。"""
        if not await Auth.revoke_token_by_id(request, token_id):
            raise HTTPException(status_code=404, detail="Token 不存在或已过期")

    @online.delete(
        "/user/{user_id}",
        summary="强制指定用户全部会话下线",
        dependencies=[Depends(Auth.has_permission("monitor:online:forceLogout"))],
        responses={200: {"model": ApiResponseDto[ForceLogoutUserResultDto]}},
    )
    async def revoke_user(
        request: Request,
        user_id: int = Path(description="需要强制下线的用户ID"),
    ):
        """强制指定用户的全部可见会话下线。"""
        revoked_count = await Auth.revoke_user_tokens(request, user_id)
        return {"user_id": user_id, "revoked_token_count": revoked_count}
