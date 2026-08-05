"""通知公告数据访问操作。"""

from fastapi import Request
from fastapi_pagination import Params, create_page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import and_, exists, func, or_
from sqlmodel import select

from module_admin.dao.tenant_scope import (
    require_tenant_id,
    tenant_clause,
    tenant_member_clause,
)
from module_admin.entity.do.notice_do import NoticeDo, NoticeRecipientDo
from module_admin.entity.do.user_do import UserDo
from module_admin.entity.notice_type import NoticeType
from utils.time_utils import now_utc8_naive


class NoticeDao:
    """持久化并查询通知公告。"""

    @staticmethod
    async def list_notices(
        request: Request,
        title: str | None,
        notice_type: NoticeType | None,
        status: str | None,
        params: Params,
    ):
        """按标题、类型和状态分页查询通知公告。"""
        query = select(NoticeDo).order_by(NoticeDo.id.desc())
        query = query.where(tenant_clause(request, NoticeDo))
        if title:
            query = query.where(NoticeDo.notice_title.contains(title))
        if notice_type:
            query = query.where(NoticeDo.notice_type == notice_type.value)
        if status is not None:
            query = query.where(NoticeDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def get_by_id(notice_id: int, request: Request) -> NoticeDo | None:
        """按编号查询通知公告。"""
        item = await request.state.mysql.get(NoticeDo, notice_id)
        tenant_id = require_tenant_id(request)
        if item is not None and item.tenant_id != tenant_id:
            return None
        return item

    @staticmethod
    def _visible_query(request: Request):
        """构造当前用户在当前租户可见的通知查询。"""
        user_id = getattr(request.state, "user_id", None)
        recipient = NoticeRecipientDo.user_id == user_id
        has_recipients = exists(
            select(NoticeRecipientDo.notice_id)
            .where(NoticeRecipientDo.notice_id == NoticeDo.id)
            .correlate(NoticeDo)
        )
        return (
            select(NoticeDo, NoticeRecipientDo.read_at)
            .outerjoin(
                NoticeRecipientDo,
                and_(
                    NoticeRecipientDo.notice_id == NoticeDo.id,
                    recipient,
                ),
            )
            .where(
                NoticeDo.status == "1",
                tenant_clause(request, NoticeDo),
                or_(~has_recipients, NoticeRecipientDo.user_id == user_id),
            )
        )

    @staticmethod
    async def create(data, request: Request) -> NoticeDo:
        """创建通知公告实体。"""
        tenant_id = require_tenant_id(request)
        notice_data = data.model_dump(
            exclude={"recipient_user_ids", "delivery_channels"}
        )
        notice_data["notice_type"] = data.notice_type.value
        item = NoticeDo(
            **notice_data,
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
                raise ValueError("通知接收人不在当前租户")
        request.state.mysql.add_all(
            [
                NoticeRecipientDo(notice_id=item.id, user_id=user_id)
                for user_id in recipient_ids
            ]
        )
        return item

    @staticmethod
    async def list_inbox(request: Request, unread_only: bool, params: Params):
        """查询当前用户可见通知及已读状态。"""
        query = NoticeDao._visible_query(request).order_by(
            NoticeDo.publish_time.desc(), NoticeDo.id.desc()
        )
        if unread_only:
            query = query.where(NoticeRecipientDo.read_at.is_(None))
        count = await request.state.mysql.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = int(count.scalar_one())
        result = await request.state.mysql.execute(
            query.offset((params.page - 1) * params.size).limit(params.size)
        )
        items = [
            {
                **notice.model_dump(),
                "read_at": read_at,
            }
            for notice, read_at in result.all()
        ]
        return create_page(items, total=total, params=params)

    @staticmethod
    async def list_latest(request: Request) -> dict[str, list[dict]]:
        """查询三类通知中各自最新的五条记录。"""
        latest: dict[str, list[dict]] = {}
        for notice_type in NoticeType:
            query = (
                NoticeDao._visible_query(request)
                .where(NoticeDo.notice_type == notice_type.value)
                .order_by(NoticeDo.publish_time.desc(), NoticeDo.id.desc())
                .limit(5)
            )
            result = await request.state.mysql.execute(query)
            latest[notice_type.value] = [
                {
                    **notice.model_dump(),
                    "read_at": read_at,
                }
                for notice, read_at in result.all()
            ]
        return latest

    @staticmethod
    async def mark_read(notice_id: int, request: Request) -> bool:
        """将当前用户可见通知标记为已读。"""
        user_id = getattr(request.state, "user_id", None)
        notice = await request.state.mysql.get(NoticeDo, notice_id)
        if (
            notice is None
            or notice.status != "1"
            or notice.tenant_id != require_tenant_id(request)
        ):
            return False
        recipient_result = await request.state.mysql.execute(
            select(NoticeRecipientDo).where(
                NoticeRecipientDo.notice_id == notice_id,
                NoticeRecipientDo.user_id == user_id,
            )
        )
        recipient = recipient_result.scalars().first()
        has_recipients = await request.state.mysql.execute(
            select(func.count())
            .select_from(NoticeRecipientDo)
            .where(NoticeRecipientDo.notice_id == notice_id)
        )
        if recipient is None and int(has_recipients.scalar_one()) > 0:
            return False
        if recipient is None:
            recipient = NoticeRecipientDo(notice_id=notice_id, user_id=user_id)
            request.state.mysql.add(recipient)
        recipient.read_at = now_utc8_naive()
        return True

    @staticmethod
    async def update(notice_id: int, data, request: Request) -> NoticeDo | None:
        """更新通知公告实体。"""
        item = await request.state.mysql.get(NoticeDo, notice_id)
        tenant_id = require_tenant_id(request)
        if item is None or item.tenant_id != tenant_id:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if data.notice_type is not None:
            update_data["notice_type"] = data.notice_type.value
        item.sqlmodel_update(update_data)
        return item

    @staticmethod
    async def delete(notice_id: int, request: Request) -> NoticeDo | None:
        """删除通知公告实体。"""
        item = await request.state.mysql.get(NoticeDo, notice_id)
        tenant_id = require_tenant_id(request)
        if item is not None and item.tenant_id == tenant_id:
            await request.state.mysql.delete(item)
        elif item is not None:
            item = None
        return item
