"""消息中心数据访问操作。"""

from datetime import datetime

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import and_, exists, func, or_
from sqlmodel import select

from module_admin.dao.tenant_scope import (
    require_tenant_id,
    tenant_clause,
    tenant_member_clause,
)
from module_admin.entity.do.message_do import MessageDo, MessageRecipientDo
from module_admin.entity.do.user_do import UserDo
from module_admin.entity.message_type import MessageReadStatus, MessageType
from utils.time_utils import now_utc8_naive


class MessageDao:
    """持久化并查询消息中心数据。"""

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
    ):
        """按管理端筛选条件分页查询消息。"""
        query = select(MessageDo).where(tenant_clause(request, MessageDo))
        if title:
            query = query.where(MessageDo.message_title.contains(title))
        if content:
            query = query.where(MessageDo.message_content.contains(content))
        if message_type:
            query = query.where(MessageDo.message_type == message_type.value)
        if status is not None:
            query = query.where(MessageDo.status == status)
        if start_time is not None:
            query = query.where(MessageDo.publish_time >= start_time)
        if end_time is not None:
            query = query.where(MessageDo.publish_time <= end_time)
        query = query.order_by(MessageDo.publish_time.desc(), MessageDo.id.desc())
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    def _visible_query(request: Request):
        """构造当前用户在当前租户可见的已发布消息查询。"""
        user_id = getattr(request.state, "user_id", None)
        recipient = MessageRecipientDo.user_id == user_id
        has_recipients = exists(
            select(MessageRecipientDo.message_id)
            .where(MessageRecipientDo.message_id == MessageDo.id)
            .correlate(MessageDo)
        )
        return (
            select(MessageDo, MessageRecipientDo.read_at)
            .outerjoin(
                MessageRecipientDo,
                and_(
                    MessageRecipientDo.message_id == MessageDo.id,
                    recipient,
                ),
            )
            .where(
                MessageDo.status == "1",
                or_(
                    MessageDo.publish_time.is_(None),
                    MessageDo.publish_time <= now_utc8_naive(),
                ),
                tenant_clause(request, MessageDo),
                or_(~has_recipients, MessageRecipientDo.user_id == user_id),
            )
        )

    @staticmethod
    async def list_my_messages(
        request: Request,
        keyword: str | None,
        message_type: MessageType | None,
        read_status: MessageReadStatus,
        start_time: datetime | None,
        end_time: datetime | None,
        params: Params,
    ):
        """分页查询当前用户可见的消息及阅读状态。"""
        query = MessageDao._visible_query(request)
        if keyword:
            query = query.where(
                or_(
                    MessageDo.message_title.contains(keyword),
                    MessageDo.message_content.contains(keyword),
                )
            )
        if message_type:
            query = query.where(MessageDo.message_type == message_type.value)
        if read_status == MessageReadStatus.UNREAD:
            query = query.where(MessageRecipientDo.read_at.is_(None))
        elif read_status == MessageReadStatus.READ:
            query = query.where(MessageRecipientDo.read_at.is_not(None))
        if start_time is not None:
            query = query.where(MessageDo.publish_time >= start_time)
        if end_time is not None:
            query = query.where(MessageDo.publish_time <= end_time)
        return await paginate(
            request.state.mysql,
            query.order_by(MessageDo.publish_time.desc(), MessageDo.id.desc()),
            params=params,
        )

    @staticmethod
    async def get_by_id(message_id: int, request: Request) -> MessageDo | None:
        """按编号查询当前租户消息。"""
        item = await request.state.mysql.get(MessageDo, message_id)
        tenant_id = require_tenant_id(request)
        if item is not None and item.tenant_id != tenant_id:
            return None
        return item

    @staticmethod
    async def get_my_by_id(
        message_id: int, request: Request
    ) -> tuple[MessageDo, datetime | None] | None:
        """查询当前用户可见的单条消息。"""
        result = await request.state.mysql.execute(
            MessageDao._visible_query(request).where(MessageDo.id == message_id)
        )
        return result.first()

    @staticmethod
    async def create(data, request: Request) -> MessageDo:
        """创建消息及指定收件人关联。"""
        tenant_id = require_tenant_id(request)
        message_data = data.model_dump(
            exclude={"recipient_user_ids", "delivery_channels"}
        )
        message_data["message_type"] = data.message_type.value
        item = MessageDo(
            **message_data,
            create_by=getattr(request.state, "user_id", None),
            tenant_id=tenant_id,
        )
        request.state.mysql.add(item)
        await request.state.mysql.flush()
        recipient_ids = list(dict.fromkeys(data.recipient_user_ids))
        if recipient_ids:
            user_result = await request.state.mysql.execute(
                select(UserDo.id).where(
                    UserDo.id.in_(recipient_ids),
                    tenant_member_clause(UserDo, tenant_id),
                    UserDo.status == "1",
                    UserDo.deleted_at.is_(None),
                )
            )
            existing_user_ids = set(user_result.scalars().all())
            if existing_user_ids != set(recipient_ids):
                raise ValueError("消息接收人不在当前租户")
        request.state.mysql.add_all(
            [
                MessageRecipientDo(message_id=item.id, user_id=user_id)
                for user_id in recipient_ids
            ]
        )
        return item

    @staticmethod
    async def list_latest(request: Request) -> dict[str, list[dict]]:
        """查询三类消息中各自最新的五条记录。"""
        latest: dict[str, list[dict]] = {}
        for message_type in MessageType:
            query = (
                MessageDao._visible_query(request)
                .where(MessageDo.message_type == message_type.value)
                .order_by(MessageDo.publish_time.desc(), MessageDo.id.desc())
                .limit(5)
            )
            result = await request.state.mysql.execute(query)
            latest[message_type.value] = [
                {
                    **message.model_dump(),
                    "read_at": read_at,
                }
                for message, read_at in result.all()
            ]
        return latest

    @staticmethod
    async def unread_count(request: Request) -> int:
        """统计当前用户可见的未读消息数量。"""
        visible = MessageDao._visible_query(request).where(
            MessageRecipientDo.read_at.is_(None)
        )
        result = await request.state.mysql.execute(
            select(func.count()).select_from(visible.subquery())
        )
        return int(result.scalar_one())

    @staticmethod
    async def mark_read(message_id: int, request: Request) -> bool:
        """将当前用户可见消息标记为已读。"""
        user_id = getattr(request.state, "user_id", None)
        result = await request.state.mysql.execute(
            MessageDao._visible_query(request).where(MessageDo.id == message_id)
        )
        visible = result.first()
        if visible is None:
            return False
        _, read_at = visible
        if read_at is not None:
            return True
        recipient_result = await request.state.mysql.execute(
            select(MessageRecipientDo).where(
                MessageRecipientDo.message_id == message_id,
                MessageRecipientDo.user_id == user_id,
            )
        )
        recipient = recipient_result.scalars().first()
        if recipient is None:
            recipient = MessageRecipientDo(message_id=message_id, user_id=user_id)
            request.state.mysql.add(recipient)
        recipient.read_at = now_utc8_naive()
        return True

    @staticmethod
    async def mark_all_read(request: Request) -> int:
        """将当前用户全部可见未读消息标记为已读。"""
        user_id = getattr(request.state, "user_id", None)
        result = await request.state.mysql.execute(
            MessageDao._visible_query(request).where(
                MessageRecipientDo.read_at.is_(None)
            )
        )
        message_ids = [message.id for message, _ in result.all()]
        if not message_ids:
            return 0
        recipient_result = await request.state.mysql.execute(
            select(MessageRecipientDo).where(
                MessageRecipientDo.message_id.in_(message_ids),
                MessageRecipientDo.user_id == user_id,
            )
        )
        recipients = {
            recipient.message_id: recipient
            for recipient in recipient_result.scalars().all()
        }
        read_at = now_utc8_naive()
        for message_id in message_ids:
            recipient = recipients.get(message_id)
            if recipient is None:
                request.state.mysql.add(
                    MessageRecipientDo(
                        message_id=message_id,
                        user_id=user_id,
                        read_at=read_at,
                    )
                )
            else:
                recipient.read_at = read_at
        return len(message_ids)

    @staticmethod
    async def update(message_id: int, data, request: Request) -> MessageDo | None:
        """更新当前租户消息。"""
        item = await MessageDao.get_by_id(message_id, request)
        if item is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if data.message_type is not None:
            update_data["message_type"] = data.message_type.value
        item.sqlmodel_update(update_data)
        return item

    @staticmethod
    async def delete(message_id: int, request: Request) -> MessageDo | None:
        """删除当前租户消息。"""
        item = await MessageDao.get_by_id(message_id, request)
        if item is not None:
            await request.state.mysql.delete(item)
        return item
