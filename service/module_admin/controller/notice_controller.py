"""通知公告接口。"""

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.notice_dto import NoticeCreateDto, NoticeDto, NoticeUpdateDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.notice_service import NoticeService


class NoticeController:
    """通知公告管理接口。"""

    notice = APIRouter(prefix="/notice", tags=["通知公告"])

    @notice.get(
        "/list",
        summary="分页查询通知公告",
        dependencies=[Depends(Auth.has_permission("system:notice:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[NoticeDto]]}},
    )
    async def list_notices(
        request: Request,
        title: str | None = Query(default=None, description="公告标题，支持模糊查询"),
        notice_type: str | None = Query(default=None, description="公告类型"),
        status: str | None = Query(
            default=None,
            pattern="^[01]$",
            description="公告状态：0停用，1正常",
        ),
        params: Params = Depends(),
    ):
        """分页查询通知公告。"""
        return await NoticeService.list_notices(
            request, title, notice_type, status, params
        )

    @notice.post(
        "/add",
        summary="新增通知公告",
        dependencies=[Depends(Auth.has_permission("system:notice:add"))],
        responses={200: {"model": ApiResponseDto[NoticeDto]}},
    )
    async def create(data: NoticeCreateDto, request: Request):
        """新增通知公告。"""
        return await NoticeService.create(data, request)

    @notice.get(
        "/{notice_id}",
        summary="查询通知公告详情",
        dependencies=[Depends(Auth.has_permission("system:notice:query"))],
        responses={200: {"model": ApiResponseDto[NoticeDto]}},
    )
    async def detail(
        request: Request,
        notice_id: int = Path(description="公告编号"),
    ):
        """查询通知公告详情。"""
        return await NoticeService.detail(notice_id, request)

    @notice.put(
        "/{notice_id}",
        summary="修改通知公告",
        dependencies=[Depends(Auth.has_permission("system:notice:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update(
        data: NoticeUpdateDto,
        request: Request,
        notice_id: int = Path(description="公告编号"),
    ):
        """修改通知公告。"""
        return await NoticeService.update(notice_id, data, request)

    @notice.delete(
        "/{notice_id}",
        summary="删除通知公告",
        dependencies=[Depends(Auth.has_permission("system:notice:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        notice_id: int = Path(description="公告编号"),
    ):
        """删除通知公告。"""
        return await NoticeService.delete(notice_id, request)
