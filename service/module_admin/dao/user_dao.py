"""用户数据访问层。"""

from datetime import datetime
from typing import Union

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import or_
from sqlmodel import delete, select

from config.env import settings
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.organization_do import (DepartmentDo, PostDo,
                                                    UserPostDo)
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDo, RoleMenuDo
from module_admin.entity.do.user_do import (PasswordResetTokenDo, UserDo,
                                            UserPasswordHistoryDo, UserRoleDo)
from module_admin.entity.dto.user_dto import (LoginUserRequestByPhoneDto,
                                              LoginUserRequestByUsernameDto,
                                              RegisterUserRequestByUsernameDto,
                                              UpdateUserRequestDto)
from module_admin.service.data_scope_service import DataScopeService
from utils.time_utils import now_utc8_naive


class UserDao:
    """用户数据访问对象。"""

    @staticmethod
    def _tenant_filter(request: Request, model):
        """为用户相关查询生成当前租户过滤条件。"""
        tenant_id = getattr(request.state, "tenant_id", None)
        return model.tenant_id == tenant_id if tenant_id is not None else True

    @staticmethod
    async def create_user_by_username(
        users: RegisterUserRequestByUsernameDto, request: Request
    ) -> UserDo:
        """
        根据用户名创建用户.

        Args:
            users (RegisterUserRequestByUsernameDto): 包含用户信息的对象，包括用户名等信息.
            request (Request): fastapi 请求对象，用于获取应用状态中的 MySQL 数据库连接.

        Returns:
            UserDo: 创建成功的用户对象.

        """
        mysql = request.state.mysql
        user_data = users.model_dump(exclude={"post_ids"})
        user_data.setdefault(
            "tenant_id",
            getattr(request.state, "tenant_id", settings.DEFAULT_TENANT_ID),
        )
        if getattr(request.state, "user_id", None) is not None:
            scope = await DataScopeService.resolve(request)
            if not scope.all_data and (
                users.dept_id is None
                or not await DataScopeService.can_access_department(
                    users.dept_id, request
                )
            ):
                raise ValueError("Department is outside the data scope")
        dept_result = (
            await mysql.execute(
                select(DepartmentDo).where(
                    DepartmentDo.dept_id == users.dept_id,
                    DepartmentDo.tenant_id == user_data["tenant_id"],
                )
            )
            if users.dept_id is not None
            else None
        )
        if users.dept_id is not None and dept_result.scalars().first() is None:
            raise ValueError("部门不存在")
        post_ids = list(dict.fromkeys(users.post_ids))
        if post_ids:
            existing_post_ids = await DataScopeService.filter_post_ids(
                request, post_ids
            )
            missing_post_ids = [post_id for post_id in post_ids if post_id not in existing_post_ids]
            if missing_post_ids:
                raise ValueError(f"岗位不存在: {missing_post_ids}")
        user = UserDo(**user_data)
        mysql.add(user)
        await mysql.flush()
        mysql.add_all([UserPostDo(user_id=user.id, post_id=post_id) for post_id in post_ids])
        return user

    @staticmethod
    async def get_user_by_username(
        users: LoginUserRequestByUsernameDto, request: Request
    ) -> Union[UserDo, None]:
        """
        根据用户名获取用户.

        Args:
            users (LoginUserRequestByUsernameDto): 包含用户信息的对象，包括用户名等信息.
            request (Request): fastapi 请求对象，用于获取应用状态中的 MySQL 数据库连接.

        Returns:
            UserDo: 用户对象.

        """
        mysql = request.state.mysql
        stmt = select(UserDo).where(UserDo.username == users.username)
        result = await mysql.execute(stmt)
        user = result.scalars().first()
        return user

    @staticmethod
    async def get_user_by_phone(
        users: LoginUserRequestByPhoneDto, request: Request
    ) -> Union[UserDo, None]:
        """根据手机号获取用户.

        Args:
            users (LoginUserRequestByPhoneDto): 包含用户信息的对象，包括手机号等信息.
            request (Request): fastapi 请求对象，用于获取应用状态中的 MySQL 数据库连接.

        Returns:
            UserDo: 用户对象.
        """
        mysql = request.state.mysql
        stmt = select(UserDo).where(UserDo.phone == users.phone)
        result = await mysql.execute(stmt)
        user = result.scalars().first()
        return user

    @staticmethod
    async def get_user_by_identifier(
        identifier: str, request: Request, tenant_id: int | None = None
    ) -> Union[UserDo, None]:
        """按用户名、邮箱或手机号查找用户。"""
        tenant_filter = UserDo.tenant_id == tenant_id if tenant_id is not None else True
        result = await request.state.mysql.execute(
            select(UserDo).where(
                or_(
                    UserDo.username == identifier,
                    UserDo.email == identifier,
                    UserDo.phone == identifier,
                ),
                tenant_filter,
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_by_external_subject(
        provider: str,
        subject: str,
        request: Request,
        tenant_id: int | None = None,
    ) -> UserDo | None:
        """按外部身份提供商和主体标识查找用户。"""
        tenant_filter = UserDo.tenant_id == tenant_id if tenant_id is not None else True
        result = await request.state.mysql.execute(
            select(UserDo).where(
                UserDo.auth_provider == provider,
                UserDo.auth_subject == subject,
                tenant_filter,
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_password_history(
        user_id: int, request: Request
    ) -> list[UserPasswordHistoryDo]:
        """读取用户最近的历史密码。"""
        result = await request.state.mysql.execute(
            select(UserPasswordHistoryDo)
            .where(UserPasswordHistoryDo.user_id == user_id)
            .order_by(UserPasswordHistoryDo.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_password_reset_token(
        token_hash: str, request: Request
    ) -> PasswordResetTokenDo | None:
        """按哈希查询未消费的密码找回令牌。"""
        result = await request.state.mysql.execute(
            select(PasswordResetTokenDo).where(
                PasswordResetTokenDo.token_hash == token_hash,
                PasswordResetTokenDo.consumed_at.is_(None),
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(user_id: int, request: Request) -> Union[UserDo, None]:
        """根据用户ID获取用户.
        Args:
            user_id (int): 用户ID.
            request (Request): fastapi 请求对象，用于获取应用状态中的 MySQL 数据库连接.

        Returns:
            UserDo: 用户对象.
        """
        mysql = request.state.mysql
        scope = await DataScopeService.resolve(request)
        filters = [UserDo.id == user_id, scope.user_id_clause(UserDo.id)]
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id is not None:
            filters.append(UserDo.tenant_id == tenant_id)
        result = await mysql.execute(select(UserDo).where(*filters))
        return result.scalars().first()

    @staticmethod
    async def get_user_roles(
        user_id: int, request: Request, enabled_only: bool = True
    ) -> list[RoleDo]:
        """返回当前关联表和旧角色字段共同关联的角色。"""
        mysql = request.state.mysql
        legacy_role_id = (
            select(UserDo.role_id).where(UserDo.id == user_id).scalar_subquery()
        )
        assigned_role_ids = select(UserRoleDo.role_id).where(
            UserRoleDo.user_id == user_id
        )
        role_query = select(RoleDo).where(
            or_(RoleDo.id == legacy_role_id, RoleDo.id.in_(assigned_role_ids))
        )
        if enabled_only:
            role_query = role_query.where(RoleDo.status == "1")
        tenant_id = getattr(request.state, "tenant_id", None)
        if tenant_id is not None:
            role_query = role_query.where(RoleDo.tenant_id == tenant_id)
        role_result = await mysql.execute(role_query)
        return list(role_result.scalars().all())

    @staticmethod
    async def get_roles_by_ids(role_ids: list[int], request: Request) -> list[RoleDo]:
        """返回与输入 ID 匹配的角色。"""
        unique_role_ids = list(dict.fromkeys(role_ids))
        if not unique_role_ids:
            return []
        result = await request.state.mysql.execute(
            select(RoleDo).where(
                RoleDo.id.in_(unique_role_ids),
                UserDao._tenant_filter(request, RoleDo),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_admin_user_ids(
        user_ids: list[int], request: Request
    ) -> set[int]:
        """返回通过任一关联方式拥有保留管理员角色的用户 ID。"""
        unique_user_ids = list(dict.fromkeys(user_ids))
        if not unique_user_ids:
            return set()

        assigned_admins = (
            select(UserRoleDo.user_id)
            .join(RoleDo, RoleDo.id == UserRoleDo.role_id)
            .where(
                UserRoleDo.user_id.in_(unique_user_ids),
                RoleDo.code == settings.ADMIN_ROLE_CODE,
                UserDao._tenant_filter(request, RoleDo),
            )
        )
        legacy_admins = (
            select(UserDo.id)
            .join(RoleDo, RoleDo.id == UserDo.role_id)
            .where(
                UserDo.id.in_(unique_user_ids),
                RoleDo.code == settings.ADMIN_ROLE_CODE,
                UserDao._tenant_filter(request, UserDo),
                UserDao._tenant_filter(request, RoleDo),
            )
        )
        result = await request.state.mysql.execute(
            assigned_admins.union(legacy_admins)
        )
        return set(result.scalars().all())

    @staticmethod
    async def get_user_info(user_id: int, request: Request) -> Union[dict, None]:
        """按用户 ID 查询用户、角色和权限信息。"""
        mysql = request.state.mysql
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            return None

        roles = await UserDao.get_user_roles(user_id, request)
        role_ids = [role.id for role in roles]
        role_data = [role.model_dump() for role in roles]
        post_result = await mysql.execute(
            select(PostDo)
            .join(UserPostDo, UserPostDo.post_id == PostDo.post_id)
            .where(
                UserPostDo.user_id == user_id,
                PostDo.tenant_id == getattr(request.state, "tenant_id", PostDo.tenant_id),
            )
            .order_by(PostDo.post_sort, PostDo.post_id)
        )
        post_data = [post.model_dump() for post in post_result.scalars().all()]

        if any(role.code == settings.ADMIN_ROLE_CODE for role in roles):
            wildcard_query = (
                select(PermissionDo.code)
                .where(PermissionDo.code == "*:*:*", PermissionDo.status == "1")
                .limit(1)
            )
            wildcard_result = await mysql.execute(wildcard_query)
            wildcard_permission = wildcard_result.scalars().first()
            if wildcard_permission:
                return {
                    "user": user.model_dump(exclude={"password"}),
                    "roles": role_data,
                    "posts": post_data,
                    "permissions": [wildcard_permission],
                }

        permissions = set()
        if role_ids:
            permission_query = (
                select(MenuDo.perms)
                .select_from(MenuDo)
                .join(RoleMenuDo, RoleMenuDo.menu_id == MenuDo.menu_id)
                .where(
                    RoleMenuDo.role_id.in_(role_ids),
                    MenuDo.status == "1",
                    MenuDo.tenant_id
                    == getattr(request.state, "tenant_id", MenuDo.tenant_id),
                    MenuDo.perms.is_not(None),
                    MenuDo.perms != "",
                )
            )
            permission_result = await mysql.execute(permission_query)
            permissions.update(permission_result.scalars().all())

        return {
            "user": user.model_dump(exclude={"password"}),
            "roles": role_data,
            "posts": post_data,
            "permissions": sorted(permissions),
        }

    @staticmethod
    async def list_users(
        request: Request,
        username: str | None,
        phone: str | None,
        email: str | None,
        nickname: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
        params: Params,
    ):
        """按条件分页查询用户。"""
        scope = await DataScopeService.resolve(request)
        query = select(
            UserDo.id,
            UserDo.create_time,
            UserDo.username,
            UserDo.email,
            UserDo.phone,
            UserDo.role_id,
            UserDo.dept_id,
            UserDo.nickname,
            UserDo.sex,
            UserDo.avatar,
            UserDo.update_time,
            UserDo.status,
        ).where(
            scope.user_id_clause(UserDo.id),
            UserDao._tenant_filter(request, UserDo),
        ).order_by(UserDo.id)
        if username:
            query = query.where(UserDo.username.contains(username))
        if phone:
            query = query.where(UserDo.phone.contains(phone))
        if email:
            query = query.where(UserDo.email.contains(email))
        if nickname:
            query = query.where(UserDo.nickname.contains(nickname))
        if start_time:
            query = query.where(UserDo.create_time >= start_time)
        if end_time:
            query = query.where(UserDo.create_time <= end_time)
        return await paginate(
            request.state.mysql,
            query,
            params=params,
            transformer=lambda rows: [dict(row._mapping) for row in rows],
        )

    @staticmethod
    async def get_user_route_menus(user_id: int, request: Request) -> list[MenuDo]:
        """查询用户可见且已启用的路由菜单。"""
        mysql = request.state.mysql
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            return []

        roles = await UserDao.get_user_roles(user_id, request)

        menu_query = (
            select(MenuDo)
            .where(
                MenuDo.status == "1",
                MenuDo.menu_type != "F",
                MenuDo.tenant_id == getattr(request.state, "tenant_id", MenuDo.tenant_id),
            )
            .order_by(MenuDo.sort, MenuDo.menu_id)
        )
        if not any(role.code == settings.ADMIN_ROLE_CODE for role in roles):
            role_ids = [role.id for role in roles]
            if not role_ids:
                return []
            menu_query = (
                menu_query.join(RoleMenuDo, RoleMenuDo.menu_id == MenuDo.menu_id)
                .where(RoleMenuDo.role_id.in_(role_ids))
            )

        result = await mysql.execute(menu_query)
        return list({menu.menu_id: menu for menu in result.scalars().all()}.values())

    @staticmethod
    async def update_user_by_id(
        user_id: int, users: UpdateUserRequestDto, request: Request
    ) -> Union[str, None]:
        """根据用户ID修改用户信息."""
        mysql = request.state.mysql
        user_db = await UserDao.get_user_by_id(user_id, request)
        if user_db is None:
            return "用户不存在"
        user_data = users.model_dump(exclude_unset=True)
        user_data.pop("role_id", None)
        post_ids = user_data.pop("post_ids", None)
        if "dept_id" in user_data:
            dept_id = user_data["dept_id"]
            scope = await DataScopeService.resolve(request)
            if not scope.all_data and (
                dept_id is None
                or not await DataScopeService.can_access_department(dept_id, request)
            ):
                return "部门不在数据权限范围内"
        if post_ids is not None:
            post_ids = list(dict.fromkeys(post_ids))
            if post_ids:
                existing_post_ids = await DataScopeService.filter_post_ids(
                    request, post_ids
                )
                missing_post_ids = [
                    post_id for post_id in post_ids if post_id not in existing_post_ids
                ]
                if missing_post_ids:
                    return f"岗位不存在: {missing_post_ids}"
            await mysql.execute(delete(UserPostDo).where(UserPostDo.user_id == user_id))
            mysql.add_all([UserPostDo(user_id=user_id, post_id=post_id) for post_id in post_ids])
        user_data["update_time"] = now_utc8_naive()
        user_db.sqlmodel_update(user_data)
        return None

    @staticmethod
    async def update_user_password_by_id(
        user_id: int, password: str, request: Request
    ) -> Union[str, None]:
        """根据用户ID修改用户密码."""
        user_db = await UserDao.get_user_by_id(user_id, request)
        if user_db is None:
            return "用户不存在"
        await UserDao._apply_password_hash(user_db, password, request)
        return None

    @staticmethod
    async def update_password_without_scope(
        user_id: int, password: str, request: Request
    ) -> Union[str, None]:
        """在无登录上下文的密码找回流程中更新密码。"""
        mysql = request.state.mysql
        user_db = await mysql.get(UserDo, user_id)
        if user_db is None:
            return "用户不存在"
        await UserDao._apply_password_hash(user_db, password, request)
        return None

    @staticmethod
    async def _apply_password_hash(user_db: UserDo, password: str, request: Request) -> None:
        """记录旧密码并更新密码版本。"""
        mysql = request.state.mysql
        if user_db.password:
            history = await UserDao.get_password_history(user_db.id, request)
            if len(history) >= settings.PASSWORD_HISTORY_COUNT > 0:
                await mysql.delete(history[-1])
            mysql.add(
                UserPasswordHistoryDo(
                    user_id=user_db.id,
                    password_hash=user_db.password,
                )
            )
        user_db.password = password
        user_db.password_changed_at = now_utc8_naive()
        user_db.must_change_password = False
        user_db.update_time = now_utc8_naive()

    @staticmethod
    async def bind_user_roles(
        user_id: int, role_ids: list[int], request: Request
    ) -> Union[str, None]:
        """替换用户的全部角色关联。"""
        mysql = request.state.mysql
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            return "用户不存在"

        unique_role_ids = list(dict.fromkeys(role_ids))
        if unique_role_ids:
            result = await mysql.execute(
                select(RoleDo.id).where(
                    RoleDo.id.in_(unique_role_ids),
                    UserDao._tenant_filter(request, RoleDo),
                )
            )
            existing_role_ids = set(result.scalars().all())
            missing_role_ids = [
                role_id
                for role_id in unique_role_ids
                if role_id not in existing_role_ids
            ]
            if missing_role_ids:
                return f"角色不存在: {missing_role_ids}"

        await mysql.execute(delete(UserRoleDo).where(UserRoleDo.user_id == user_id))
        mysql.add_all(
            [
                UserRoleDo(user_id=user_id, role_id=role_id)
                for role_id in unique_role_ids
            ]
        )
        user.role_id = None
        user.update_time = now_utc8_naive()
        return None

    @staticmethod
    async def batch_update_user_status(
        user_ids: list[int], status: str, request: Request
    ) -> Union[str, None]:
        """批量启用或停用用户。"""
        mysql = request.state.mysql
        unique_user_ids = list(dict.fromkeys(user_ids))
        scope = await DataScopeService.resolve(request)
        result = await mysql.execute(
            select(UserDo).where(
                UserDo.id.in_(unique_user_ids),
                scope.user_id_clause(UserDo.id),
                UserDao._tenant_filter(request, UserDo),
            )
        )
        users = result.scalars().all()
        existing_user_ids = {user.id for user in users}
        missing_user_ids = [
            user_id for user_id in unique_user_ids if user_id not in existing_user_ids
        ]
        if missing_user_ids:
            return f"用户不存在: {missing_user_ids}"

        update_time = now_utc8_naive()
        for user in users:
            user.status = status
            user.update_time = update_time
        return None

    @staticmethod
    async def batch_delete_users(
        user_ids: list[int], request: Request
    ) -> Union[str, None]:
        """在一个事务中删除用户及其角色关联。"""
        mysql = request.state.mysql
        unique_user_ids = list(dict.fromkeys(user_ids))
        scope = await DataScopeService.resolve(request)
        result = await mysql.execute(
            select(UserDo.id).where(
                UserDo.id.in_(unique_user_ids),
                scope.user_id_clause(UserDo.id),
                UserDao._tenant_filter(request, UserDo),
            )
        )
        existing_user_ids = set(result.scalars().all())
        missing_user_ids = [
            user_id for user_id in unique_user_ids if user_id not in existing_user_ids
        ]
        if missing_user_ids:
            return f"用户不存在: {missing_user_ids}"

        await mysql.execute(
            delete(UserRoleDo).where(UserRoleDo.user_id.in_(unique_user_ids))
        )
        await mysql.execute(
            delete(UserPostDo).where(UserPostDo.user_id.in_(unique_user_ids))
        )
        await mysql.execute(
            delete(UserDo).where(
                UserDo.id.in_(unique_user_ids),
                UserDao._tenant_filter(request, UserDo),
            )
        )
        return None

    @staticmethod
    async def delete_user_by_id(
        user_id: int, request: Request
    ) -> Union[str, None]:
        """删除一个用户及其全部角色关联。"""
        mysql = request.state.mysql
        user = await UserDao.get_user_by_id(user_id, request)
        if user is None:
            return "用户不存在"

        await mysql.execute(delete(UserRoleDo).where(UserRoleDo.user_id == user_id))
        await mysql.execute(delete(UserPostDo).where(UserPostDo.user_id == user_id))
        await mysql.delete(user)
        return None
