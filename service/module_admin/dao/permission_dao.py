"""权限数据访问层。"""

from fastapi import Request
from sqlalchemy import or_
from sqlmodel import select

from config.env import settings
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDo
from module_admin.entity.do.role_do import RoleMenuDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo


class PermissionDao:
    """权限查询方法。"""

    @staticmethod
    async def has_permission(
        user_id: int, permission_code: str, request: Request
    ) -> bool:
        """先检查超级管理员通配权限，再检查精确菜单权限。"""
        mysql = request.state.mysql
        wildcard_stmt = (
            select(PermissionDo.id)
            .select_from(PermissionDo)
            .join(RoleDo, RoleDo.code == settings.ADMIN_ROLE_CODE)
            .outerjoin(UserRoleDo, UserRoleDo.role_id == RoleDo.id)
            .outerjoin(UserDo, UserDo.role_id == RoleDo.id)
            .where(
                PermissionDo.code == "*:*:*",
                PermissionDo.status == "1",
                RoleDo.status == "1",
                or_(UserRoleDo.user_id == user_id, UserDo.id == user_id),
            )
            .limit(1)
        )
        wildcard_result = await mysql.execute(wildcard_stmt)
        if wildcard_result.scalars().first() is not None:
            return True

        stmt = (
            select(MenuDo.menu_id)
            .select_from(MenuDo)
            .join(PermissionDo, PermissionDo.code == MenuDo.perms)
            .join(RoleMenuDo, RoleMenuDo.menu_id == MenuDo.menu_id)
            .join(RoleDo, RoleDo.id == RoleMenuDo.role_id)
            .outerjoin(UserRoleDo, UserRoleDo.role_id == RoleDo.id)
            .outerjoin(UserDo, UserDo.role_id == RoleDo.id)
            .where(
                MenuDo.perms == permission_code,
                MenuDo.menu_type == "F",
                MenuDo.status == "1",
                PermissionDo.code == permission_code,
                PermissionDo.status == "1",
                RoleDo.status == "1",
                or_(UserRoleDo.user_id == user_id, UserDo.id == user_id),
            )
            .limit(1)
        )
        result = await mysql.execute(stmt)
        return result.scalars().first() is not None
