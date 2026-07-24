"""租户管理和租户切换接口。"""

from fastapi import APIRouter, Depends, Path, Query, Request

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.dto.tenant_dto import (
    TenantCreateDto,
    TenantDto,
    TenantMemberAddDto,
    TenantMemberDto,
    TenantMemberUpdateDto,
    TenantSwitchDto,
    TenantUpdateDto,
)
from module_admin.service.tenant_service import TenantService


class TenantController:
    """租户生命周期、成员关系和租户切换接口。"""

    tenant = APIRouter(prefix="/tenant", tags=["租户管理"])

    @tenant.get(
        "/list",
        summary="查询我的租户",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[list[TenantDto]]}},
    )
    async def list_current(request: Request):
        """查询当前用户可访问的租户。"""
        return await TenantService.list_current_user(request)

    @tenant.get(
        "/list/all",
        summary="查询全部租户",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:list")),
        ],
        responses={200: {"model": ApiResponseDto[list[TenantDto]]}},
    )
    async def list_all(request: Request):
        """查询平台管理员可见的租户。"""
        return await TenantService.list_all(request)

    @tenant.post(
        "/switch",
        summary="切换当前租户",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def switch(data: TenantSwitchDto, request: Request):
        """签发目标租户上下文的新令牌。"""
        return await TenantService.switch(data.tenant_id, request)

    @tenant.post(
        "/add",
        summary="新增租户",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:add")),
        ],
        responses={200: {"model": ApiResponseDto[TenantDto]}},
    )
    async def create(data: TenantCreateDto, request: Request):
        """新增租户并绑定当前用户。"""
        return await TenantService.create(data, request)

    @tenant.put(
        "/{tenant_id}",
        summary="修改租户",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:edit")),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update(
        data: TenantUpdateDto,
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
    ):
        """按乐观锁版本更新租户。"""
        return await TenantService.update(tenant_id, data, request)

    @tenant.delete(
        "/{tenant_id}",
        summary="删除租户",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:remove")),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
        version: int = Query(ge=1, description="乐观锁版本号"),
    ):
        """按版本号软删除租户。"""
        return await TenantService.delete(tenant_id, version, request)

    @tenant.get(
        "/{tenant_id}/members",
        summary="查询租户成员",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:member:list")),
        ],
        responses={200: {"model": ApiResponseDto[list[TenantMemberDto]]}},
    )
    async def members(
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
    ):
        """查询租户成员关系。"""
        return await TenantService.members(tenant_id, request)

    @tenant.post(
        "/{tenant_id}/members",
        summary="添加租户成员",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:member:add")),
        ],
        responses={200: {"model": ApiResponseDto[TenantMemberDto]}},
    )
    async def add_member(
        data: TenantMemberAddDto,
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
    ):
        """添加用户到租户。"""
        return await TenantService.add_member(tenant_id, data, request)

    @tenant.put(
        "/{tenant_id}/members/{user_id}",
        summary="修改租户成员",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:member:edit")),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_member(
        data: TenantMemberUpdateDto,
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
        user_id: int = Path(gt=0, description="用户编号"),
    ):
        """按版本号修改租户成员。"""
        return await TenantService.update_member(tenant_id, user_id, data, request)

    @tenant.delete(
        "/{tenant_id}/members/{user_id}",
        summary="移除租户成员",
        dependencies=[
            Depends(Auth.platform_admin_status),
            Depends(Auth.has_permission("system:tenant:member:remove")),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def remove_member(
        request: Request,
        tenant_id: int = Path(gt=0, description="租户编号"),
        user_id: int = Path(gt=0, description="用户编号"),
        version: int = Query(ge=1, description="乐观锁版本号"),
    ):
        """软删除租户成员关系。"""
        data = TenantMemberUpdateDto(status="0", is_default=False, version=version)
        return await TenantService.update_member(tenant_id, user_id, data, request)
