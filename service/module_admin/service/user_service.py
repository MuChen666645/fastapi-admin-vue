"""User Service Model"""

from datetime import datetime
from typing import Union

from fastapi import Request, HTTPException
from fastapi_pagination import Params
from module_admin.entity.dto.user_dto import (
    RegisterUserRequestByUsernameDto,
    LoginUserRequestByUsernameDto,
    TokenDto,
    LoginUserRequestByPhoneDto,
    UpdateUserRequestDto,
    UpdateUserPasswordRequestDto,
    BatchUpdateUserStatusDto,
    BatchUserIdsDto,
    BindUserRolesDto,
)
from module_admin.dao.user_dao import UserDao
from utils.fastapi_admin import FastApiAdmin
from module_admin.auth.authorization import Auth
from module_admin.service.code_service import CodeService
from module_admin.service.login_security_service import LoginSecurityService
from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import LoginLogDo


class UserService:
    ADMIN_USER_PROTECTION_MESSAGE = "禁止非超级管理员操作超级管理员用户"

    @staticmethod
    def _has_admin_role(roles: list) -> bool:
        return Auth.has_admin_role(roles)

    @staticmethod
    async def _get_actor_roles(request: Request) -> list:
        return await Auth.get_actor_roles(request)

    @staticmethod
    async def _ensure_can_manage_users(
        user_ids: list[int],
        request: Request,
        actor_roles: list | None = None,
    ) -> bool:
        """Reject non-admin mutations targeting any super-admin user."""
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
        try:
            await LogDao.create_login(
                LoginLogDo(
                    user_id=user_id,
                    username=username,
                    ip_address=Auth.get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    status=status,
                    message=message,
                ),
                request,
            )
        except Exception:
            # Audit storage must never change the authentication result.
            return

    @staticmethod
    async def _ensure_login_ip_allowed(request: Request, identifier: str) -> None:
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
    async def _reject_invalid_password(
        request: Request,
        identifier: str,
        user_id: int,
    ) -> None:
        try:
            await LoginSecurityService.record_password_failure(request)
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
    async def create_user_by_username_services(
        users: RegisterUserRequestByUsernameDto, request: Request
    ) -> None:
        """
        通过用户名创建用户服务.

        Args:
            users (RegisterUserRequestByUsernameDto): 包含用户名和密码的用户注册请求对象.
            request (Request): 请求对象.
        """
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
        await UserService._ensure_login_ip_allowed(request, users.username)
        user = await UserDao.get_user_by_username(users, request)
        if user is None:
            await UserService._record_login(request, users.username, "0", "用户名不存在")
            raise HTTPException(status_code=404, detail="用户名不存在")
        if not FastApiAdmin.verify_password(users.password, user.password):
            await UserService._reject_invalid_password(
                request,
                users.username,
                user.id,
            )
        await LoginSecurityService.clear_password_failures(request)
        await CodeService.verify_captcha_services(
            users.captcha_id,
            users.captcha,
            request,
        )
        await UserService._ensure_login_ip_allowed(request, users.username)
        token = await Auth.create_login_token(
            {"user_id": user.id, "username": user.username}, request
        )
        await UserService._record_login(
            request, user.username, "1", "登录成功", user.id
        )
        return TokenDto(access_token=token)

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
        if not FastApiAdmin.verify_password(users.password, user.password):
            await UserService._reject_invalid_password(
                request,
                users.phone,
                user.id,
            )
        await LoginSecurityService.clear_password_failures(request)
        await CodeService.verify_captcha_services(
            users.captcha_id,
            users.captcha,
            request,
        )
        await UserService._ensure_login_ip_allowed(request, users.phone)
        token = await Auth.create_login_token(
            {"user_id": str(user.id), "username": user.username}, request
        )
        await UserService._record_login(
            request, user.username, "1", "登录成功", user.id
        )
        return TokenDto(access_token=token)

    @staticmethod
    async def get_user_by_id_services(
        user_id: int, request: Request
    ) -> dict:
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
        return user_info

    @staticmethod
    async def get_current_user_info_services(request: Request) -> dict:
        """Get current login user info."""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")

        user_info = await UserDao.get_user_info(user_id, request)
        if user_info is None:
            raise HTTPException(status_code=404, detail="User Not Found")
        return user_info

    @staticmethod
    async def get_current_user_routes_services(request: Request) -> list[dict]:
        """Get current login user frontend routes."""
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
        """Query paged users."""
        return await UserDao.list_users(
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
    async def update_user_by_id_services(
        user_id: int, users: UpdateUserRequestDto, request: Request
    ) -> None:
        """通过用户ID修改用户信息服务."""
        await UserService._ensure_can_manage_users([user_id], request)
        result = await UserDao.update_user_by_id(user_id, users, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
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
        new_password = FastApiAdmin.password_hash(users.new_password)
        result = await UserDao.update_user_password_by_id(
            user_id, new_password, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def bind_user_roles_services(
        user_id: int, roles: BindUserRolesDto, request: Request
    ) -> None:
        """Replace all role bindings for a user."""
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

        disabled_role_ids = [
            role.id for role in requested_roles if role.status != "1"
        ]
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

        result = await UserDao.bind_user_roles(
            user_id, requested_role_ids, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def batch_update_user_status_services(
        users: BatchUpdateUserStatusDto, request: Request
    ) -> None:
        """Batch enable or disable users."""
        await UserService._ensure_can_manage_users(users.user_ids, request)
        result = await UserDao.batch_update_user_status(
            users.user_ids, users.status, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def batch_delete_users_services(
        users: BatchUserIdsDto, request: Request
    ) -> None:
        """Batch delete users."""
        await UserService._ensure_can_manage_users(users.user_ids, request)
        result = await UserDao.batch_delete_users(users.user_ids, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def delete_user_by_id_services(user_id: int, request: Request) -> None:
        """Delete a user by ID."""
        await UserService._ensure_can_manage_users([user_id], request)
        result = await UserDao.delete_user_by_id(user_id, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def logout_services(request: Request, authorization: str | None) -> None:
        """Revoke the current login token."""
        await Auth.revoke_login_token(request, authorization)
        return None
