"""用户接口控制器。"""

from datetime import datetime
from typing import Annotated

from fastapi import (APIRouter, Depends, FastAPI, Form, Header, Path, Query,
                     Request)
from fastapi_pagination import Page, Params

from config.env import settings
from config.rate_limit import limiter
from module_admin.auth.authorization import Auth
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.dto.user_dto import (BatchUpdateUserStatusDto,
                                              BatchUserIdsDto,
                                              BindUserRolesDto,
                                              LoginUserRequestByPhoneDto,
                                              LoginUserRequestByUsernameDto,
                                              RegisterUserRequestByUsernameDto,
                                              ResetUserPasswordRequestDto,
                                              TokenDto,
                                              UpdateUserPasswordRequestDto,
                                              UpdateUserRequestDto,
                                              UserInfoDto, UserInfoUserDto,
                                              UserRouteDto)
from module_admin.service.user_service import UserService


class UserController:
    """用户接口控制器。"""

    user = APIRouter(tags=["用户模块"], prefix="/user")

    def __init__(self, app: FastAPI):
        """保存应用实例并完成控制器初始化。"""
        self.app = app
        super().__init__()

    @staticmethod
    @user.post(
        "/add",
        summary="创建用户",
        dependencies=[Depends(Auth.has_permission("system:user:add"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_user(users: RegisterUserRequestByUsernameDto, request: Request):
        """创建用户。"""
        return await UserService.create_user_by_username_services(users, request)

    @staticmethod
    @user.post(
        "/login/username",
        summary="用户名登录",
        responses={200: {"model": ApiResponseDto[TokenDto]}},
    )
    @limiter.limit(settings.RATE_LIMIT_LOGIN)
    async def login_user(
        users: Annotated[LoginUserRequestByUsernameDto, Form()], request: Request
    ):
        """使用用户名登录。"""
        return await UserService.get_user_by_username_services(users, request)

    @staticmethod
    @user.post(
        "/login/phone",
        summary="手机号密码登录",
        responses={200: {"model": ApiResponseDto[TokenDto]}},
    )
    @limiter.limit(settings.RATE_LIMIT_LOGIN)
    async def login_user_by_phone(
        users: Annotated[LoginUserRequestByPhoneDto, Form()], request: Request
    ):
        """使用手机号登录。"""
        return await UserService.get_user_by_phone_services(users, request)

    @staticmethod
    @user.post(
        "/logout",
        summary="退出登录",
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def logout(
        request: Request,
        Authorization: str | None = Header(default=None, description="Token"),
    ):
        """撤销当前登录 Token。"""
        return await UserService.logout_services(request, Authorization)

    @staticmethod
    @user.get(
        "/info",
        summary="获取当前用户信息",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[UserInfoDto]}},
    )
    async def get_current_user_info(request: Request):
        """获取当前用户信息。"""
        return await UserService.get_current_user_info_services(request)

    @staticmethod
    @user.get(
        "/routes",
        summary="获取当前用户路由菜单",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[list[UserRouteDto]]}},
    )
    async def get_current_user_routes(request: Request):
        """获取当前用户的前端动态路由。"""
        return await UserService.get_current_user_routes_services(request)

    @staticmethod
    @user.put(
        "/batch/status",
        summary="批量启用或禁用用户",
        dependencies=[Depends(Auth.has_permission("system:user:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def batch_update_user_status(
        users: BatchUpdateUserStatusDto, request: Request
    ):
        """批量启用或停用用户。"""
        return await UserService.batch_update_user_status_services(users, request)

    @staticmethod
    @user.delete(
        "/batch",
        summary="批量删除用户",
        dependencies=[Depends(Auth.has_permission("system:user:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def batch_delete_users(users: BatchUserIdsDto, request: Request):
        """批量删除用户。"""
        return await UserService.batch_delete_users_services(users, request)

    @staticmethod
    @user.put(
        "/{user_id}/roles",
        summary="绑定用户角色",
        dependencies=[
            Depends(Auth.has_permission("system:user:edit")),
            Depends(Auth.has_permission("system:role:edit")),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def bind_user_roles(
        roles: BindUserRolesDto,
        request: Request,
        user_id: int = Path(description="用户ID"),
    ):
        """替换用户的全部角色关联。"""
        return await UserService.bind_user_roles_services(user_id, roles, request)

    @staticmethod
    @user.get(
        "/list",
        summary="查询用户列表",
        dependencies=[Depends(Auth.has_permission("system:user:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[UserInfoUserDto]]}},
    )
    async def list_users(
        request: Request,
        username: str | None = Query(default=None, description="用户名，支持模糊查询"),
        phone: str | None = Query(default=None, description="手机号，支持模糊查询"),
        email: str | None = Query(default=None, description="邮箱，支持模糊查询"),
        nickname: str | None = Query(default=None, description="昵称，支持模糊查询"),
        start_time: datetime | None = Query(default=None, description="创建开始时间"),
        end_time: datetime | None = Query(default=None, description="创建结束时间"),
        params: Params = Depends(),
    ):
        """分页查询用户。"""
        return await UserService.list_users_services(
            request,
            username,
            phone,
            email,
            nickname,
            start_time,
            end_time,
            params,
        )

    @staticmethod
    @user.get(
        "/{user_id}",
        summary="获取用户信息",
        dependencies=[Depends(Auth.has_permission("system:user:query"))],
        responses={200: {"model": ApiResponseDto[UserInfoDto]}},
    )
    async def get_user_by_id(
        request: Request, user_id: int = Path(description="用户ID")
    ):
        """按 ID 查询用户。"""
        return await UserService.get_user_by_id_services(user_id, request)

    @staticmethod
    @user.delete(
        "/{user_id}",
        summary="删除用户",
        dependencies=[Depends(Auth.has_permission("system:user:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_user_by_id(
        request: Request, user_id: int = Path(description="用户ID")
    ):
        """按 ID 删除用户。"""
        return await UserService.delete_user_by_id_services(user_id, request)

    @staticmethod
    @user.put(
        "/{user_id}",
        summary="修改用户信息",
        dependencies=[Depends(Auth.has_permission("system:user:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_user_by_id(
        users: UpdateUserRequestDto,
        request: Request,
        user_id: int = Path(description="用户ID"),
    ):
        """按 ID 修改用户信息。"""
        return await UserService.update_user_by_id_services(user_id, users, request)

    @staticmethod
    @user.put(
        "/{user_id}/password",
        summary="修改用户密码",
        dependencies=[Depends(Auth.has_permission("system:user:resetPwd"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_user_password_by_id(
        users: UpdateUserPasswordRequestDto,
        request: Request,
        user_id: int = Path(description="用户ID"),
    ):
        """按 ID 修改用户密码。"""
        return await UserService.update_user_password_by_id_services(
            user_id, users, request
        )

    @staticmethod
    @user.put(
        "/{user_id}/reset-password",
        summary="管理员重置用户密码",
        dependencies=[Depends(Auth.has_permission("system:user:resetPwd"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def reset_user_password(
        users: ResetUserPasswordRequestDto,
        request: Request,
        user_id: int = Path(description="用户ID"),
    ):
        """由有权限的管理员重置目标用户密码。"""
        return await UserService.reset_user_password_services(user_id, users, request)
