"""权限数据访问层。"""

from fastapi import Request
from sqlalchemy import or_
from sqlmodel import select

from config.env import settings
from module_admin.dao.tenant_scope import current_tenant_id, tenant_clause
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDo, RoleMenuDo, RolePermissionDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo


class PermissionDao:
    """权限查询方法。"""

    @staticmethod
    def _role_assignment_filter(user_id: int):
        """按现代用户角色关联和历史角色字段匹配用户角色。"""
        legacy_role_id = (
            select(UserDo.role_id).where(UserDo.id == user_id).scalar_subquery()
        )
        assigned_role_ids = select(UserRoleDo.role_id).where(
            UserRoleDo.user_id == user_id
        )
        return or_(
            RoleDo.id == legacy_role_id,
            RoleDo.id.in_(assigned_role_ids),
        )

    @staticmethod
    def _user_tenant_filter(user_id: int, tenant_id: int | None, request: Request):
        """确保权限主体用户属于当前租户。"""
        if tenant_id is None:
            return False
        return (
            select(UserDo.id)
            .where(
                UserDo.id == user_id,
                tenant_clause(request, UserDo),
            )
            .exists()
        )

    @staticmethod
    def _role_tenant_filter(tenant_id: int | None):
        """确保授权角色属于当前租户。"""
        return RoleDo.tenant_id == tenant_id if tenant_id is not None else False

    @staticmethod
    async def has_permission(
        user_id: int, permission_code: str, request: Request
    ) -> bool:
        """先检查超级管理员通配权限，再检查精确菜单权限。"""
        mysql = request.state.mysql
        tenant_id = current_tenant_id(request)
        role_assignment = PermissionDao._role_assignment_filter(user_id)
        user_tenant = PermissionDao._user_tenant_filter(user_id, tenant_id, request)
        role_tenant = PermissionDao._role_tenant_filter(tenant_id)
        wildcard_stmt = (
            select(PermissionDo.id)
            .select_from(PermissionDo)
            .join(RoleDo, RoleDo.code == settings.ADMIN_ROLE_CODE)
            .where(
                PermissionDo.code == "*:*:*",
                PermissionDo.status == "1",
                RoleDo.status == "1",
                role_assignment,
                user_tenant,
                role_tenant,
            )
            .limit(1)
        )
        stmt = (
            select(MenuDo.menu_id)
            .select_from(MenuDo)
            .join(PermissionDo, PermissionDo.code == MenuDo.perms)
            .join(RoleMenuDo, RoleMenuDo.menu_id == MenuDo.menu_id)
            .join(RoleDo, RoleDo.id == RoleMenuDo.role_id)
            .where(
                MenuDo.perms == permission_code,
                MenuDo.menu_type == "F",
                MenuDo.status == "1",
                PermissionDo.code == permission_code,
                PermissionDo.status == "1",
                RoleDo.status == "1",
                role_assignment,
                user_tenant,
                role_tenant,
                tenant_clause(request, MenuDo),
            )
            .limit(1)
        )
        wildcard_result = await mysql.execute(wildcard_stmt)
        if wildcard_result.scalars().first() is not None:
            return True
        result = await mysql.execute(stmt)
        return result.scalars().first() is not None

    @staticmethod
    async def has_field_permission(
        user_id: int,
        resource: str,
        field_name: str,
        request: Request,
    ) -> bool:
        """检查字段级权限，不依赖菜单关联。"""
        mysql = request.state.mysql
        permission_code = f"field:{resource}:{field_name}"
        tenant_id = current_tenant_id(request)
        role_assignment = PermissionDao._role_assignment_filter(user_id)
        user_tenant = PermissionDao._user_tenant_filter(user_id, tenant_id, request)
        role_tenant = PermissionDao._role_tenant_filter(tenant_id)
        wildcard_query = (
            select(PermissionDo.id)
            .select_from(PermissionDo)
            .join(RoleDo, RoleDo.code == settings.ADMIN_ROLE_CODE)
            .where(
                PermissionDo.code == "*:*:*",
                PermissionDo.status == "1",
                RoleDo.status == "1",
                role_assignment,
                user_tenant,
                role_tenant,
            )
            .limit(1)
        )
        wildcard_result = await mysql.execute(wildcard_query)
        if wildcard_result.scalars().first() is not None:
            return True
        query = (
            select(PermissionDo.id)
            .select_from(PermissionDo)
            .join(RolePermissionDo, RolePermissionDo.permission_id == PermissionDo.id)
            .join(RoleDo, RoleDo.id == RolePermissionDo.role_id)
            .where(
                PermissionDo.code == permission_code,
                PermissionDo.permission_type == "field",
                PermissionDo.status == "1",
                RoleDo.status == "1",
                role_assignment,
                user_tenant,
                role_tenant,
            )
            .limit(1)
        )
        result = await mysql.execute(query)
        return result.scalars().first() is not None
