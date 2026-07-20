"""通知公告数据访问操作。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.notice_do import NoticeDo


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
        return await request.state.mysql.get(NoticeDo, notice_id)

    @staticmethod
    async def create(data, request: Request) -> NoticeDo:
        """创建通知公告实体。"""
        item = NoticeDo(
            **data.model_dump(),
            create_by=getattr(request.state, "user_id", None),
        )
        request.state.mysql.add(item)
        return item

    @staticmethod
    async def update(notice_id: int, data, request: Request) -> NoticeDo | None:
        """更新通知公告实体。"""
        item = await request.state.mysql.get(NoticeDo, notice_id)
        if item is None:
            return None
        item.sqlmodel_update(data.model_dump(exclude_unset=True))
        return item

    @staticmethod
    async def delete(notice_id: int, request: Request) -> NoticeDo | None:
        """删除通知公告实体。"""
        item = await request.state.mysql.get(NoticeDo, notice_id)
        if item is not None:
            await request.state.mysql.delete(item)
        return item
