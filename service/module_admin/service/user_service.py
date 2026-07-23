"""用户业务服务。"""

from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.log_dao import LogDao
from module_admin.dao.permission_dao import PermissionDao
from module_admin.dao.tenant_dao import TenantDao
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.log_do import LoginLogDo
from module_admin.entity.dto.user_dto import (
    BatchUpdateUserStatusDto,
    BatchUserIdsDto,
    BindUserRolesDto,
    LoginUserRequestByPhoneDto,
    LoginUserRequestByUsernameDto,
    RefreshTokenRequestDto,
    RegisterUserRequestByUsernameDto,
    ResetUserPasswordRequestDto,
    TokenDto,
    UpdateUserPasswordRequestDto,
    UpdateUserRequestDto,
)
from module_admin.service.code_service import CodeService
from module_admin.service.idempotency_service import IdempotencyService
from module_admin.service.login_security_service import LoginSecurityService
from module_admin.service.mfa_service import MfaService
from module_admin.service.password_policy import (
    PasswordPolicyError,
    matches_history,
    validate_password,
)
from utils.fastapi_admin import FastApiAdmin
from utils.time_utils import now_utc8_naive


class UserService:
    """编排用户认证、资料管理、角色绑定和路由生成业务。"""

    # 非超级管理员触发保护时统一返回该提示，避免不同入口行为不一致。
    ADMIN_USER_PROTECTION_MESSAGE = "禁止非超级管理员操作超级管理员用户"

    @staticmethod
    def _has_admin_role(roles: list) -> bool:
        """判断角色列表是否包含配置的超级管理员角色。"""
        return Auth.has_admin_role(roles)

    @staticmethod
    async def _get_actor_roles(request: Request) -> list:
        """读取当前请求操作者的已启用角色。"""
        return await Auth.get_actor_roles(request)

    @staticmethod
    async def _ensure_can_manage_users(
        user_ids: list[int],
        request: Request,
        actor_roles: list | None = None,
    ) -> bool:
        """拒绝非超级管理员修改任何超级管理员用户。"""
        roles = actor_roles
        if roles is None:
            roles = await UserService._get_actor_roles(request)
        actor_is_admin = UserService._has_admin_role(roles)
        if actor_is_admin:
            return True

        admin_user_ids = await UserDao.get_admin_user_ids(user_ids, request)
        if admin_user_ids:
            raise HTTPException(
                status_code=403,
                detail=UserService.ADMIN_USER_PROTECTION_MESSAGE,
            )
        return False

    @staticmethod
    def _menu_to_route(menu: dict) -> dict:
        """将菜单数据转换为前端动态路由节点。"""
        path = menu.get("menu_path") or ""
        route = {
            "id": menu.get("menu_id"),
            "parent_id": menu.get("parent_id"),
            "path": path,
            "name": menu.get("menu_name") or path.strip("/").replace("/", "-"),
            "component": menu.get("component"),
            "redirect": None,
            "hidden": str(menu.get("is_hidden")) == "1",
            "meta": {
                "title": menu.get("menu_name") or "",
                "icon": menu.get("icon"),
                "noCache": str(menu.get("is_cache")) != "1",
                "link": menu.get("link_url"),
            },
            "children": [],
        }
        if menu.get("menu_type") in {"L", "W"} and menu.get("link_url"):
            route["meta"]["link"] = menu.get("link_url")
        return route

    @staticmethod
    def _build_route_tree(menus: list) -> list[dict]:
        """把扁平菜单列表组装成前端需要的路由树。"""
        routes = [UserService._menu_to_route(menu.model_dump()) for menu in menus]
        route_map = {route["id"]: route for route in routes}
        tree = []
        for route in routes:
            parent = route_map.get(route.get("parent_id"))
            if parent is None or route.get("parent_id") == route.get("id"):
                tree.append(route)
            else:
                parent["children"].append(route)
        for route in routes:
            route.pop("id", None)
            route.pop("parent_id", None)
        return tree

    @staticmethod
    async def _record_login(
        request: Request,
        username: str,
        status: str,
        message: str,
        user_id: int | None = None,
    ) -> None:
        """记录登录结果，且不让审计存储故障影响认证结果。"""
        try:
            await LogDao.create_login(
                LoginLogDo(
                    user_id=user_id,
                    tenant_id=getattr(request.state, "tenant_id", None),
                    username=username,
                    ip_address=Auth.get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    status=status,
                    message=message,
                ),
                request,
            )
        except Exception:
            # 审计存储故障不能改变认证结果。
            return

    @staticmethod
    async def _ensure_login_ip_allowed(request: Request, identifier: str) -> None:
        """检查登录 IP 锁定状态，并记录被拒绝的登录尝试。"""
        try:
            await LoginSecurityService.ensure_ip_allowed(request)
        except HTTPException as exc:
            await UserService._record_login(
                request,
                identifier,
                "0",
                str(exc.detail),
            )
            raise

    @staticmethod
    async def _ensure_login_account_allowed(
        request: Request, identifier: int | str
    ) -> None:
        """检查账号锁定状态，并记录被拒绝的登录尝试。"""
        if not getattr(request, "app", None):
            return
        try:
            await LoginSecurityService.ensure_account_allowed(request, identifier)
        except HTTPException as exc:
            await UserService._record_login(
                request,
                str(identifier),
                "0",
                str(exc.detail),
            )
            raise

    @staticmethod
    async def _reject_invalid_password(
        request: Request,
        identifier: str,
        user_id: int,
    ) -> None:
        """记录密码错误并在达到阈值时抛出 IP 锁定异常。"""
        try:
            await LoginSecurityService.record_password_failure(request)
            await LoginSecurityService.record_password_failure(request, user_id)
        except HTTPException as exc:
            await UserService._record_login(
                request,
                identifier,
                "0",
                str(exc.detail),
                user_id,
            )
            raise
        await UserService._record_login(
            request,
            identifier,
            "0",
            "密码错误",
            user_id,
        )
        raise HTTPException(status_code=401, detail="密码错误")

    @staticmethod
    async def _validate_new_password(password: str, user, request: Request) -> None:
        """执行密码策略和历史密码校验。"""
        try:
            validate_password(password, getattr(user, "username", None))
        except PasswordPolicyError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        if settings.PASSWORD_HISTORY_COUNT <= 0:
            return
        history = await UserDao.get_password_history(user.id, request)
        if matches_history(
            password,
            (item.password_hash for item in history),
            FastApiAdmin.verify_password,
        ):
            raise HTTPException(status_code=400, detail="新密码不能重复使用历史密码")

    @staticmethod
    async def _ensure_user_enabled(request: Request, user, identifier: str) -> None:
        """拒绝停用账号登录，并记录登录失败原因。"""
        if str(getattr(user, "status", None)) != "1":
            await UserService._record_login(
                request,
                identifier,
                "0",
                "用户已停用",
                user.id,
            )
            raise HTTPException(status_code=403, detail="用户已停用")

    @staticmethod
    async def _set_login_tenant(request: Request, user) -> None:
        """建立本地登录的租户上下文并拒绝不可用租户。"""
        tenant_id = getattr(user, "tenant_id", None)
        request.state.tenant_id = tenant_id
        if (
            tenant_id is None
            or await TenantDao.get(tenant_id, request) is None
            or await TenantDao.get_member(user.id, tenant_id, request) is None
        ):
            await UserService._record_login(
                request,
                user.username,
                "0",
                "租户不可用",
                user.id,
            )
            raise HTTPException(status_code=403, detail="当前租户不可用")

    @staticmethod
    async def _create_token_response(user, request: Request) -> TokenDto:
        """为用户创建访问令牌和刷新令牌。"""
        password_changed_at_value = getattr(user, "password_changed_at", None)
        if (
            settings.PASSWORD_MAX_AGE_DAYS > 0
            and password_changed_at_value is not None
            and password_changed_at_value
            < now_utc8_naive() - timedelta(days=settings.PASSWORD_MAX_AGE_DAYS)
        ):
            user.must_change_password = True
        password_changed_at = (
            password_changed_at_value.isoformat()
            if password_changed_at_value is not None
            else None
        )
        access_token, refresh_token = await Auth.create_login_token_pair(
            {
                "user_id": user.id,
                "username": user.username,
                "tenant_id": getattr(request.state, "tenant_id", None)
                or getattr(user, "tenant_id", None),
                "password_changed_at": password_changed_at,
                "must_change_password": bool(
                    getattr(user, "must_change_password", False)
                ),
            },
            request,
        )
        return TokenDto(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            must_change_password=bool(getattr(user, "must_change_password", False)),
        )

    @staticmethod
    async def create_user_by_username_services(
        users: RegisterUserRequestByUsernameDto, request: Request
    ) -> None:
        """
        通过用户名创建用户服务.

        Args:
            users (RegisterUserRequestByUsernameDto): 包含用户名和密码的用户注册请求对象.
            request (Request): 请求对象.
        """
        try:
            validate_password(users.password, users.username)
        except PasswordPolicyError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        users.password = FastApiAdmin.password_hash(users.password)
        try:
            await UserDao.create_user_by_username(users, request)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return None

    @staticmethod
    async def get_user_by_username_services(
        users: LoginUserRequestByUsernameDto, request: Request
    ) -> Union[TokenDto, str]:
        """校验用户名登录请求并签发登录 Token。"""
        await UserService._ensure_login_ip_allowed(request, users.username)
        user = await UserDao.get_user_by_username(users, request)
        if user is None:
            await UserService._record_login(
                request, users.username, "0", "用户名不存在"
            )
            raise HTTPException(status_code=404, detail="用户名不存在")
        await UserService._set_login_tenant(request, user)
        await UserService._ensure_login_account_allowed(request, user.id)
        if not FastApiAdmin.verify_password(users.password, user.password):
            await UserService._reject_invalid_password(
                request,
                users.username,
                user.id,
            )
        await LoginSecurityService.clear_password_failures(request)
        await LoginSecurityService.clear_password_failures(request, user.id)
        await CodeService.verify_captcha_services(
            users.captcha_id,
            users.captcha,
            request,
        )
        await UserService._ensure_login_ip_allowed(request, users.username)
        await UserService._ensure_user_enabled(request, user, users.username)
        await MfaService.verify_login(user, users.mfa_code, request)
        await UserService._record_login(
            request, user.username, "1", "登录成功", user.id
        )
        return await UserService._create_token_response(user, request)

    @staticmethod
    async def get_user_by_phone_services(
        users: LoginUserRequestByPhoneDto, request: Request
    ) -> TokenDto:
        """
        通过手机号获取用户服务.
        Args:
            users (LoginUserRequestByPhoneDto): 包含手机号和验证码的用户登录请求对象.
            request (Request): 请求对象.
        Returns:
        TokenDto: 包含访问令牌的对象.
        """
        await UserService._ensure_login_ip_allowed(request, users.phone)
        user = await UserDao.get_user_by_phone(users, request)
        if user is None:
            await UserService._record_login(request, users.phone, "0", "用户不存在")
            raise HTTPException(status_code=404, detail="用户不存在")
        await UserService._set_login_tenant(request, user)
        await UserService._ensure_login_account_allowed(request, user.id)
        if not FastApiAdmin.verify_password(users.password, user.password):
            await UserService._reject_invalid_password(
                request,
                users.phone,
                user.id,
            )
        await LoginSecurityService.clear_password_failures(request)
        await LoginSecurityService.clear_password_failures(request, user.id)
        await CodeService.verify_captcha_services(
            users.captcha_id,
            users.captcha,
            request,
        )
        await UserService._ensure_login_ip_allowed(request, users.phone)
        await UserService._ensure_user_enabled(request, user, users.phone)
        await MfaService.verify_login(user, users.mfa_code, request)
        await UserService._record_login(
            request, user.username, "1", "登录成功", user.id
        )
        return await UserService._create_token_response(user, request)

    @staticmethod
    async def refresh_token_services(
        users: RefreshTokenRequestDto, request: Request
    ) -> TokenDto:
        """轮换 Refresh Token 并返回新的令牌对。"""
        access_token, refresh_token, must_change = await Auth.refresh_login_token(
            users.refresh_token,
            request,
        )
        return TokenDto(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            must_change_password=must_change,
        )

    @staticmethod
    async def setup_mfa_services(request: Request):
        """初始化当前用户 MFA。"""
        return await MfaService.setup(request)

    @staticmethod
    async def enable_mfa_services(code: str, request: Request) -> None:
        """启用当前用户 MFA。"""
        await MfaService.enable(code, request)

    @staticmethod
    async def disable_mfa_services(code: str, request: Request) -> None:
        """关闭当前用户 MFA。"""
        await MfaService.disable(code, request)

    @staticmethod
    async def get_user_by_id_services(user_id: int, request: Request) -> dict:
        """通过用户ID获取用户信息服务.

        Args:
            user_id (int): 用户ID.
            request (Request): 请求对象.

        Returns:
            ResponseUserInfoDto: 包含用户信息的对象.
        """
        user_info = await UserDao.get_user_info(user_id, request)
        if user_info is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        return await UserService._sanitize_user_info(user_info, request)

    @staticmethod
    async def _sanitize_user_info(user_info: dict, request: Request) -> dict:
        """按字段权限隐藏用户敏感字段。"""
        user = user_info.get("user")
        if not isinstance(user, dict):
            return user_info
        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            return user_info
        for field_name in ("email", "phone", "avatar"):
            if not await PermissionDao.has_field_permission(
                int(actor_user_id), "user", field_name, request
            ):
                user[field_name] = None
        return user_info

    @staticmethod
    async def get_current_user_info_services(request: Request) -> dict:
        """获取当前登录用户信息。"""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")

        user_info = await UserDao.get_user_info(user_id, request)
        if user_info is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        return await UserService._sanitize_user_info(user_info, request)

    @staticmethod
    async def get_current_user_routes_services(request: Request) -> list[dict]:
        """获取当前登录用户的前端动态路由。"""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")
        menus = await UserDao.get_user_route_menus(user_id, request)
        return UserService._build_route_tree(menus)

    @staticmethod
    async def list_users_services(
        request: Request,
        username: str | None,
        phone: str | None,
        email: str | None,
        nickname: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
        params: Params,
    ):
        """分页查询用户列表。"""
        page = await UserDao.list_users(
            request,
            username,
            phone,
            email,
            nickname,
            start_time,
            end_time,
            params,
        )
        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            field_permissions = {
                field_name: False for field_name in ("email", "phone", "avatar")
            }
        else:
            field_permissions = {
                field_name: await PermissionDao.has_field_permission(
                    int(actor_user_id), "user", field_name, request
                )
                for field_name in ("email", "phone", "avatar")
            }
        items = [
            {
                **item,
                **{
                    field_name: item.get(field_name) if allowed else None
                    for field_name, allowed in field_permissions.items()
                },
            }
            for item in page.items
        ]
        return page.model_copy(update={"items": items})

    @staticmethod
    async def update_user_by_id_services(
        user_id: int, users: UpdateUserRequestDto, request: Request
    ) -> None:
        """通过用户ID修改用户信息服务."""
        await UserService._ensure_can_manage_users([user_id], request)
        result = await UserDao.update_user_by_id(user_id, users, request)
        if result is not None:
            status_code = 409 if result == "USER_VERSION_CONFLICT" else 404
            raise HTTPException(status_code=status_code, detail=result)
        await IdempotencyService.record_batch(
            request,
            "user_update",
            "user",
            [user_id],
            None,
            users.model_dump(exclude_unset=True, exclude={"version"}),
        )
        return None

    @staticmethod
    async def update_user_password_by_id_services(
        user_id: int, users: UpdateUserPasswordRequestDto, request: Request
    ) -> None:
        """通过用户ID修改用户密码服务."""
        await UserService._ensure_can_manage_users([user_id], request)
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        if not FastApiAdmin.verify_password(users.old_password, user.password):
            raise HTTPException(status_code=401, detail="旧密码错误")
        if users.old_password == users.new_password:
            raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
        await UserService._validate_new_password(users.new_password, user, request)
        new_password = FastApiAdmin.password_hash(users.new_password)
        result = await UserDao.update_user_password_by_id(
            user_id, new_password, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        await Auth.revoke_user_tokens(request, user_id)
        return None

    @staticmethod
    async def change_current_password_services(
        users: UpdateUserPasswordRequestDto, request: Request
    ) -> None:
        """允许已登录账号完成强制改密或自助改密。"""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        if not FastApiAdmin.verify_password(users.old_password, user.password):
            raise HTTPException(status_code=401, detail="旧密码错误")
        if users.old_password == users.new_password:
            raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
        await UserService._validate_new_password(users.new_password, user, request)
        result = await UserDao.update_user_password_by_id(
            user_id,
            FastApiAdmin.password_hash(users.new_password),
            request,
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        await Auth.revoke_user_tokens(request, user_id)

    @staticmethod
    async def reset_user_password_services(
        user_id: int, users: ResetUserPasswordRequestDto, request: Request
    ) -> None:
        """在无需旧密码的情况下重置权限范围内用户的密码。"""
        await UserService._ensure_can_manage_users([user_id], request)
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        await UserService._validate_new_password(users.password, user, request)
        password = FastApiAdmin.password_hash(users.password)
        result = await UserDao.update_user_password_by_id(user_id, password, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)

            # 重置密码会使已有会话失效，避免旧凭据通过已签发 Token 继续使用。
        await Auth.revoke_user_tokens(request, user_id)
        return None

    @staticmethod
    async def bind_user_roles_services(
        user_id: int, roles: BindUserRolesDto, request: Request
    ) -> None:
        """替换用户的全部角色关联。"""
        target_user = await UserDao.get_user_by_id(user_id, request)
        if target_user is None:
            raise HTTPException(status_code=404, detail="用户不存在")

        actor_roles = await UserService._get_actor_roles(request)
        actor_is_admin = await UserService._ensure_can_manage_users(
            [user_id],
            request,
            actor_roles,
        )

        requested_role_ids = list(dict.fromkeys(roles.role_ids))
        requested_roles = await UserDao.get_roles_by_ids(requested_role_ids, request)
        requested_role_map = {role.id: role for role in requested_roles}
        missing_role_ids = [
            role_id
            for role_id in requested_role_ids
            if role_id not in requested_role_map
        ]
        if missing_role_ids:
            raise HTTPException(
                status_code=404, detail=f"角色不存在: {missing_role_ids}"
            )

        disabled_role_ids = [role.id for role in requested_roles if role.status != "1"]
        if disabled_role_ids:
            raise HTTPException(
                status_code=400, detail=f"角色已停用: {disabled_role_ids}"
            )

        if not actor_is_admin:
            if UserService._has_admin_role(requested_roles):
                raise HTTPException(status_code=403, detail="禁止授予超级管理员角色")

            actor_role_ids = {role.id for role in actor_roles}
            unauthorized_role_ids = [
                role_id
                for role_id in requested_role_ids
                if role_id not in actor_role_ids
            ]
            if unauthorized_role_ids:
                raise HTTPException(
                    status_code=403,
                    detail=f"无权授予角色: {unauthorized_role_ids}",
                )

        result = await UserDao.bind_user_roles(user_id, requested_role_ids, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def batch_update_user_status_services(
        users: BatchUpdateUserStatusDto, request: Request
    ) -> None:
        """批量启用或停用用户。"""
        await UserService._ensure_can_manage_users(users.user_ids, request)
        result = await UserDao.batch_update_user_status(
            users.user_ids, users.status, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        await IdempotencyService.record_batch(
            request,
            "user_status_update",
            "user",
            users.user_ids,
            None,
            {"status": users.status},
        )
        return None

    @staticmethod
    async def batch_delete_users_services(
        users: BatchUserIdsDto, request: Request
    ) -> None:
        """批量删除用户。"""
        await UserService._ensure_can_manage_users(users.user_ids, request)
        result = await UserDao.batch_delete_users(users.user_ids, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        await IdempotencyService.record_batch(
            request,
            "user_soft_delete",
            "user",
            users.user_ids,
            None,
            {"status": "0", "deleted": True},
        )
        return None

    @staticmethod
    async def delete_user_by_id_services(user_id: int, request: Request) -> None:
        """按 ID 删除用户。"""
        await UserService._ensure_can_manage_users([user_id], request)
        result = await UserDao.delete_user_by_id(user_id, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def logout_services(request: Request, authorization: str | None) -> None:
        """撤销当前登录 Token。"""
        await Auth.revoke_login_token(request, authorization)
        return None
