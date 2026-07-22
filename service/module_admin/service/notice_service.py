"""通知公告业务服务。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from module_admin.dao.notice_dao import NoticeDao


class NoticeService:
    """协调通知公告的生命周期操作。"""

    @staticmethod
    async def list_notices(request: Request, title, notice_type, status, params: Params):
        """分页查询通知公告。"""
        return await NoticeDao.list_notices(request, title, notice_type, status, params)

    @staticmethod
    async def detail(notice_id: int, request: Request):
        """查询通知公告详情。"""
        item = await NoticeDao.get_by_id(notice_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="通知公告不存在")
        return item

    @staticmethod
    async def create(data, request: Request):
        """创建通知公告。"""
        return await NoticeDao.create(data, request)

    @staticmethod
    async def list_inbox(request: Request, unread_only: bool, params: Params):
        """查询当前用户通知收件箱。"""
        return await NoticeDao.list_inbox(request, unread_only, params)

    @staticmethod
    async def mark_read(notice_id: int, request: Request) -> None:
        """标记当前用户通知为已读。"""
        if not await NoticeDao.mark_read(notice_id, request):
            raise HTTPException(status_code=404, detail="通知公告不存在或不可见")

    @staticmethod
    async def update(notice_id: int, data, request: Request):
        """更新通知公告。"""
        if await NoticeDao.update(notice_id, data, request) is None:
            raise HTTPException(status_code=404, detail="通知公告不存在")

    @staticmethod
    async def delete(notice_id: int, request: Request):
        """删除通知公告。"""
        if await NoticeDao.delete(notice_id, request) is None:
            raise HTTPException(status_code=404, detail="通知公告不存在")
