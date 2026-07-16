""" 角色模块控制器. """

from fastapi import APIRouter, Depends, FastAPI, Path, Query, Request
from module_admin.service.role_service import RoleService
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.dto.role_dto import (
    BatchUpdateRoleStatusDto,
    CreateRoleDto,
    RoleDetailDto,
    RoleListDto,
    UpdataRoleDto,
)
from module_admin.auth.authorization import Auth
from fastapi_pagination import Page, Params


class RoleController:
    """RoleController."""

    role = APIRouter(tags=["角色模块"], prefix="/role")

    def __init__(self, app: FastAPI):
        """Constructor."""
        self.app = app
        super().__init__()

    @staticmethod
    @role.post(
        "/add",
        summary="创建角色",
        dependencies=[Depends(Auth.has_permission("system:role:add"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_role(roles: CreateRoleDto, request: Request):
        """创建角色."""
        return await RoleService.create_role_services(roles, request)

    @staticmethod
    @role.get(
        "/list",
        dependencies=[Depends(Auth.has_permission("system:role:list"))],
        summary="获取角色列表",
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[RoleListDto]]}},
    )
    async def get_role_by_all(
        request: Request,
        name: str = Query(default=None, description="角色名称"),
        code: str = Query(default=None, description="角色编码"),
        params: Params = Depends(),
    ):
        """获取角色列表."""
        return await RoleService.get_role_by_all_services(request, name, code, params)

    @staticmethod
    @role.put(
        "/batch/status",
        summary="批量启用或禁用角色",
        dependencies=[Depends(Auth.has_permission("system:role:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def batch_update_role_status(roles: BatchUpdateRoleStatusDto, request: Request):
        """批量启用或禁用角色."""
        return await RoleService.batch_update_role_status_services(roles, request)

    @staticmethod
    @role.get(
        "/{role_id}",
        summary="根据ID查询角色",
        dependencies=[Depends(Auth.has_permission("system:role:query"))],
        responses={200: {"model": ApiResponseDto[RoleDetailDto]}},
    )
    async def get_role_by_id(
        request: Request, role_id: int = Path(description="角色ID")
    ):
        """根据ID获取角色."""
        return await RoleService.get_role_by_id_services(role_id, request)

    @staticmethod
    @role.delete(
        "/{role_id}",
        dependencies=[Depends(Auth.has_permission("system:role:remove"))],
        summary="删除角色",
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def del_role_by_id(
        request: Request, role_id: int = Path(description="角色ID")
    ):
        """根据ID删除角色."""
        return await RoleService.del_role_by_id_services(role_id, request)

    @staticmethod
    @role.put(
        "/{role_id}",
        summary="修改角色信息",
        dependencies=[Depends(Auth.has_permission("system:role:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def upd_role_by_id(
        roles: UpdataRoleDto,
        request: Request,
        role_id: int = Path(description="角色ID"),
    ):
        """更新角色信息."""
        return await RoleService.upd_role_by_id_services(roles, request, role_id)
