"""消息中心业务服务。"""

from datetime import datetime

from fastapi import HTTPException, Request
from fastapi_pagination import Page, Params, create_page

from module_admin.dao.message_dao import MessageDao
from module_admin.entity.dto.message_dto import (
    MessageDto,
    MessageItemDto,
    MessageLatestDto,
    MessageReadAllDto,
    MessageUnreadCountDto,
)
from module_admin.entity.message_type import MessageReadStatus, MessageType
from module_admin.service.notification_service import NotificationService


class MessageService:
    """协调消息发布、投递和个人阅读状态。"""

    @staticmethod
    async def list_messages(
        request: Request,
        title: str | None,
        content: str | None,
        message_type: MessageType | None,
        status: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
        params: Params,
    ) -> Page[MessageDto]:
        """分页查询租户消息。"""
        page = await MessageDao.list_messages(
            request,
            title,
            content,
            message_type,
            status,
            start_time,
            end_time,
            params,
        )
        items = [MessageDto.model_validate(item) for item in page.items]
        return create_page(items, total=page.total, params=params)

    @staticmethod
    async def list_my_messages(
        request: Request,
        keyword: str | None,
        message_type: MessageType | None,
        read_status: MessageReadStatus,
        start_time: datetime | None,
        end_time: datetime | None,
        params: Params,
    ) -> Page[MessageItemDto]:
        """分页查询当前用户的消息中心。"""
        page = await MessageDao.list_my_messages(
            request,
            keyword,
            message_type,
            read_status,
            start_time,
            end_time,
            params,
        )
        items = [
            MessageItemDto.model_validate({**message.model_dump(), "read_at": read_at})
            for message, read_at in page.items
        ]
        return create_page(items, total=page.total, params=params)

    @staticmethod
    async def detail(message_id: int, request: Request) -> MessageDto:
        """查询租户消息详情。"""
        item = await MessageDao.get_by_id(message_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="消息不存在")
        return MessageDto.model_validate(item)

    @staticmethod
    async def my_detail(message_id: int, request: Request) -> MessageItemDto:
        """查询当前用户可见的消息详情。"""
        item = await MessageDao.get_my_by_id(message_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="消息不存在或不可见")
        message, read_at = item
        return MessageItemDto.model_validate(
            {**message.model_dump(), "read_at": read_at}
        )

    @staticmethod
    async def create(data, request: Request) -> MessageDto:
        """创建消息并建立渠道投递任务。"""
        message = await MessageDao.create(data, request)
        await NotificationService.enqueue(message, data, request)
        return MessageDto.model_validate(message)

    @staticmethod
    async def list_latest(request: Request) -> MessageLatestDto:
        """查询系统通知、审批消息和报警提醒各自最新的五条消息。"""
        latest = await MessageDao.list_latest(request)
        return MessageLatestDto(
            **{
                message_type.value: [
                    MessageItemDto.model_validate(item)
                    for item in latest[message_type.value]
                ]
                for message_type in MessageType
            }
        )

    @staticmethod
    async def unread_count(request: Request) -> MessageUnreadCountDto:
        """查询当前用户未读消息数。"""
        return MessageUnreadCountDto(
            unread_count=await MessageDao.unread_count(request)
        )

    @staticmethod
    async def mark_read(message_id: int, request: Request) -> None:
        """标记当前用户消息为已读。"""
        if not await MessageDao.mark_read(message_id, request):
            raise HTTPException(status_code=404, detail="消息不存在或不可见")

    @staticmethod
    async def mark_all_read(request: Request) -> MessageReadAllDto:
        """标记当前用户全部可见消息为已读。"""
        return MessageReadAllDto(updated_count=await MessageDao.mark_all_read(request))

    @staticmethod
    async def update(message_id: int, data, request: Request) -> None:
        """更新租户消息。"""
        if await MessageDao.update(message_id, data, request) is None:
            raise HTTPException(status_code=404, detail="消息不存在")

    @staticmethod
    async def delete(message_id: int, request: Request) -> None:
        """删除租户消息。"""
        if await MessageDao.delete(message_id, request) is None:
            raise HTTPException(status_code=404, detail="消息不存在")
