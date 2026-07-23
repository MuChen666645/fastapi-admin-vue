"""通知公告数据访问操作。"""

from fastapi import Request
from fastapi_pagination import Params, create_page
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import and_, exists, func, or_
from sqlmodel import select

from module_admin.dao.tenant_scope import require_tenant_id, tenant_clause
from module_admin.entity.do.notice_do import NoticeDo, NoticeRecipientDo
from module_admin.entity.do.user_do import UserDo
from utils.time_utils import now_utc8_naive


class NoticeDao:
    """持久化并查询通知公告。"""

    @staticmethod
    async def list_notices(
        request: Request,
        title: str | None,
        notice_type: str | None,
        status: str | None,
        params: Params,
    ):
        """按标题、类型和状态分页查询通知公告。"""
        query = select(NoticeDo).order_by(NoticeDo.id.desc())
        query = query.where(tenant_clause(request, NoticeDo))
        if title:
            query = query.where(NoticeDo.notice_title.contains(title))
        if notice_type:
            query = query.where(NoticeDo.notice_type == notice_type)
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
    async def create(data, request: Request) -> NoticeDo:
        """创建通知公告实体。"""
        tenant_id = require_tenant_id(request)
        item = NoticeDo(
            **data.model_dump(exclude={"recipient_user_ids", "delivery_channels"}),
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
                    UserDo.tenant_id == tenant_id,
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
        user_id = getattr(request.state, "user_id", None)
        recipient = NoticeRecipientDo.user_id == user_id
        has_recipients = exists(
            select(NoticeRecipientDo.notice_id).where(
                NoticeRecipientDo.notice_id == NoticeDo.id
            )
        )
        query = (
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
            .order_by(NoticeDo.publish_time.desc(), NoticeDo.id.desc())
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
        item.sqlmodel_update(data.model_dump(exclude_unset=True))
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
