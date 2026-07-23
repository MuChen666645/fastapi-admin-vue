"""用户接口控制器。"""

from datetime import datetime
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    Path,
    Query,
    Request,
    UploadFile,
)
from fastapi_pagination import Page, Params

from config.env import settings
from config.rate_limit import limiter
from module_admin.auth.authorization import Auth
from module_admin.entity.dto.mfa_dto import MfaCodeDto, MfaSetupDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.dto.user_dto import (
    BatchUpdateUserStatusDto,
    BatchUserIdsDto,
    BindUserRolesDto,
    ConfirmPasswordResetRequestDto,
    ForgotPasswordRequestDto,
    LoginUserRequestByPhoneDto,
    LoginUserRequestByUsernameDto,
    RefreshTokenRequestDto,
    RegisterUserRequestByUsernameDto,
    ResetUserPasswordRequestDto,
    TokenDto,
    UpdateUserPasswordRequestDto,
    UpdateUserRequestDto,
    UserInfoDto,
    UserInfoUserDto,
    UserRouteDto,
)
from module_admin.service.excel_service import ExcelService
from module_admin.service.export_service import ExportService
from module_admin.service.password_reset_service import PasswordResetService
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
        "/token/refresh",
        summary="轮换刷新令牌",
        responses={200: {"model": ApiResponseDto[TokenDto]}},
    )
    @limiter.limit(settings.RATE_LIMIT_REFRESH_TOKEN)
    async def refresh_token(users: RefreshTokenRequestDto, request: Request):
        """消费旧 Refresh Token 并签发新的令牌对。"""
        return await UserService.refresh_token_services(users, request)

    @staticmethod
    @user.post(
        "/password/forgot",
        summary="申请找回密码",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    @limiter.limit(settings.RATE_LIMIT_PASSWORD_RESET)
    async def forgot_password(
        data: ForgotPasswordRequestDto,
        request: Request,
    ):
        """通过邮箱或短信申请一次性密码找回令牌。"""
        return await PasswordResetService.request_reset(data, request)

    @staticmethod
    @user.post(
        "/password/reset",
        summary="确认找回密码",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    @limiter.limit(settings.RATE_LIMIT_PASSWORD_RESET)
    async def confirm_password_reset(
        data: ConfirmPasswordResetRequestDto,
        request: Request,
    ):
        """消费密码找回令牌并设置新密码。"""
        return await PasswordResetService.confirm_reset(data, request)

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
    @user.post(
        "/mfa/setup",
        summary="初始化多因素认证",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[MfaSetupDto]}},
    )
    async def setup_mfa(request: Request):
        """生成当前账号的 TOTP 密钥和恢复码。"""
        return await UserService.setup_mfa_services(request)

    @staticmethod
    @user.post(
        "/mfa/enable",
        summary="启用多因素认证",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def enable_mfa(data: MfaCodeDto, request: Request):
        """验证 TOTP 后启用当前账号 MFA。"""
        return await UserService.enable_mfa_services(data.code, request)

    @staticmethod
    @user.post(
        "/mfa/disable",
        summary="关闭多因素认证",
        dependencies=[Depends(Auth.login_status)],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def disable_mfa(data: MfaCodeDto, request: Request):
        """验证 TOTP 后关闭当前账号 MFA。"""
        return await UserService.disable_mfa_services(data.code, request)

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
        "/me/password",
        summary="修改当前用户密码",
        dependencies=[Depends(Auth.allow_password_change)],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def change_current_password(
        users: UpdateUserPasswordRequestDto,
        request: Request,
    ):
        """修改当前账号密码并清理旧会话。"""
        return await UserService.change_current_password_services(users, request)

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
    @user.post(
        "/export/async",
        summary="创建异步用户导出任务",
        dependencies=[Depends(Auth.has_permission("system:user:list"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def create_async_user_export(request: Request):
        """创建持久化的用户 Excel 导出任务。"""
        return await ExportService.create("users", request)

    @staticmethod
    @user.get(
        "/export/tasks/{task_id}",
        summary="查询异步用户导出任务",
        dependencies=[Depends(Auth.has_permission("system:user:list"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def get_async_user_export(task_id: str, request: Request):
        """查询当前用户创建的导出任务状态。"""
        return await ExportService.get_task(task_id, request)

    @staticmethod
    @user.get(
        "/export/tasks/{task_id}/download",
        summary="下载异步用户导出文件",
        dependencies=[Depends(Auth.has_permission("system:user:list"))],
        response_model=None,
    )
    async def download_async_user_export(task_id: str, request: Request):
        """下载已完成的用户导出文件。"""
        return await ExportService.get_download(task_id, request)

    @staticmethod
    @user.get(
        "/export",
        summary="导出用户 Excel",
        dependencies=[Depends(Auth.has_permission("system:user:list"))],
        response_model=None,
    )
    async def export_users(request: Request):
        """导出当前租户可见的用户。"""
        return await ExcelService.export_users(request)

    @user.post(
        "/import",
        summary="导入用户 Excel",
        dependencies=[Depends(Auth.has_permission("system:user:add"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def import_users(
        request: Request,
        file: UploadFile = File(..., description="用户 Excel 文件"),
    ):
        """按用户 DTO 和密码策略导入用户。"""
        return await ExcelService.import_users(file, request)

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
