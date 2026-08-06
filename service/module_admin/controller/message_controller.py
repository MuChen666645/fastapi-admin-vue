"""消息中心接口。"""

from datetime import datetime

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.message_dto import (
    MessageCreateDto,
    MessageDto,
    MessageItemDto,
    MessageLatestDto,
    MessageReadAllDto,
    MessageUnreadCountDto,
    MessageUpdateDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.message_type import MessageReadStatus, MessageType
from module_admin.service.message_service import MessageService


class MessageController:
    """消息中心管理和个人消息接口。"""

    message = APIRouter(prefix="/message", tags=["消息中心"])

    @message.get(
        "/list",
        summary="分页查询消息",
        dependencies=[Depends(Auth.has_permission("system:message:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[MessageDto]]}},
    )
    async def list_messages(
        request: Request,
        title: str | None = Query(default=None, description="消息标题，支持模糊查询"),
        content: str | None = Query(default=None, description="消息内容，支持模糊查询"),
        message_type: MessageType | None = Query(default=None, description="消息类型"),
        status: str | None = Query(
            default=None,
            pattern="^[01]$",
            description="消息状态：0停用，1正常",
        ),
        start_time: datetime | None = Query(default=None, description="发布时间开始"),
        end_time: datetime | None = Query(default=None, description="发布时间结束"),
        params: Params = Depends(),
    ):
        """分页查询当前租户消息。"""
        return await MessageService.list_messages(
            request,
            title,
            content,
            message_type,
            status,
            start_time,
            end_time,
            params,
        )

    @message.post(
        "/add",
        summary="新增消息",
        dependencies=[Depends(Auth.has_permission("system:message:add"))],
        responses={200: {"model": ApiResponseDto[MessageDto]}},
    )
    async def create(data: MessageCreateDto, request: Request):
        """新增消息并创建投递任务。"""
        return await MessageService.create(data, request)

    @message.get(
        "/latest",
        summary="查询最新消息",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[MessageLatestDto]}},
    )
    async def latest(request: Request):
        """查询三类消息各自最新的五条记录。"""
        return await MessageService.list_latest(request)

    @message.get(
        "/unread-count",
        summary="查询未读消息数",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[MessageUnreadCountDto]}},
    )
    async def unread_count(request: Request):
        """查询当前用户可见的未读消息数量。"""
        return await MessageService.unread_count(request)

    @message.get(
        "/my/list",
        summary="分页查询我的消息",
        dependencies=[Depends(Auth.login_status)],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[MessageItemDto]]}},
    )
    async def list_my_messages(
        request: Request,
        keyword: str | None = Query(default=None, description="标题或内容关键词"),
        message_type: MessageType | None = Query(default=None, description="消息类型"),
        read_status: MessageReadStatus = Query(
            default=MessageReadStatus.ALL,
            description="阅读状态：all全部，unread未读，read已读",
        ),
        start_time: datetime | None = Query(default=None, description="发布时间开始"),
        end_time: datetime | None = Query(default=None, description="发布时间结束"),
        params: Params = Depends(),
    ):
        """分页查询当前用户可见的消息。"""
        return await MessageService.list_my_messages(
            request,
            keyword,
            message_type,
            read_status,
            start_time,
            end_time,
            params,
        )

    @message.get(
        "/my/{message_id}",
        summary="查询我的消息详情",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[MessageItemDto]}},
    )
    async def my_detail(
        request: Request,
        message_id: int = Path(description="消息编号"),
    ):
        """查询当前用户可见的消息详情。"""
        return await MessageService.my_detail(message_id, request)

    @message.post(
        "/read-all",
        summary="全部标记为已读",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[MessageReadAllDto]}},
    )
    async def mark_all_read(request: Request):
        """将当前用户全部可见消息标记为已读。"""
        return await MessageService.mark_all_read(request)

    @message.post(
        "/{message_id}/read",
        summary="标记消息已读",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def mark_read(
        request: Request,
        message_id: int = Path(description="消息编号"),
    ):
        """标记当前用户可见消息为已读。"""
        return await MessageService.mark_read(message_id, request)

    @message.get(
        "/{message_id}",
        summary="查询消息详情",
        dependencies=[Depends(Auth.has_permission("system:message:query"))],
        responses={200: {"model": ApiResponseDto[MessageDto]}},
    )
    async def detail(
        request: Request,
        message_id: int = Path(description="消息编号"),
    ):
        """查询当前租户消息详情。"""
        return await MessageService.detail(message_id, request)

    @message.put(
        "/{message_id}",
        summary="修改消息",
        dependencies=[Depends(Auth.has_permission("system:message:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update(
        data: MessageUpdateDto,
        request: Request,
        message_id: int = Path(description="消息编号"),
    ):
        """修改当前租户消息。"""
        return await MessageService.update(message_id, data, request)

    @message.delete(
        "/{message_id}",
        summary="删除消息",
        dependencies=[Depends(Auth.has_permission("system:message:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        message_id: int = Path(description="消息编号"),
    ):
        """删除当前租户消息。"""
        return await MessageService.delete(message_id, request)
