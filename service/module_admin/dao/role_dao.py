from typing import Union

from fastapi import Request
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import false, update
from sqlmodel import delete, select

from module_admin.dao.tenant_scope import (
    current_tenant_id,
    require_tenant_id,
    tenant_clause,
)
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.organization_do import DepartmentDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import (
    RoleDeptDo,
    RoleDo,
    RoleMenuDo,
    RolePermissionDo,
)
from module_admin.entity.dto.role_dto import CreateRoleDto, RoleListDto, UpdataRoleDto
from utils.time_utils import now_utc8_naive


class RoleCodeConflictError(ValueError):
    """角色编码已经被其他角色使用。"""


class RoleVersionConflictError(ValueError):
    """角色版本已被其他请求更新。"""


class RoleDao:
    """持久化角色及其菜单、部门关联记录。"""

    @staticmethod
    async def _validate_dept_ids(
        mysql, dept_ids: list[int], tenant_id: int | None = None
    ) -> list[int]:
        """去重部门 ID，并拒绝不存在的部门。"""
        unique_dept_ids = list(dict.fromkeys(dept_ids))
        if not unique_dept_ids:
            return []

        result = await mysql.execute(
            select(DepartmentDo.dept_id).where(
                DepartmentDo.dept_id.in_(unique_dept_ids),
                (
                    DepartmentDo.tenant_id == tenant_id
                    if tenant_id is not None
                    else false()
                ),
            )
        )
        existing_ids = set(result.scalars().all())
        missing_ids = [
            dept_id for dept_id in unique_dept_ids if dept_id not in existing_ids
        ]
        if missing_ids:
            raise ValueError(f"Department does not exist: {missing_ids}")
        return unique_dept_ids

    @staticmethod
    async def _validate_menu_ids(
        mysql, menu_ids: list[int], tenant_id: int | None = None
    ) -> list[int]:
        """校验菜单存在性后返回去重的菜单 ID。"""
        unique_menu_ids = list(dict.fromkeys(menu_ids))
        if not unique_menu_ids:
            return []

        result = await mysql.execute(
            select(MenuDo.menu_id).where(
                MenuDo.menu_id.in_(unique_menu_ids),
                MenuDo.tenant_id == tenant_id if tenant_id is not None else false(),
            )
        )
        existing_menu_ids = set(result.scalars().all())
        missing_menu_ids = [
            menu_id for menu_id in unique_menu_ids if menu_id not in existing_menu_ids
        ]
        if missing_menu_ids:
            raise ValueError(f"菜单不存在: {missing_menu_ids}")
        return unique_menu_ids

    @staticmethod
    async def _validate_field_permission_codes(
        mysql, permission_codes: list[str]
    ) -> list[str]:
        """只允许绑定字段权限目录，避免角色关联任意 API 权限。"""
        unique_codes = list(dict.fromkeys(permission_codes))
        if not unique_codes:
            return []
        invalid_codes = [code for code in unique_codes if not code.startswith("field:")]
        if invalid_codes:
            raise ValueError(f"Invalid field permission codes: {invalid_codes}")
        result = await mysql.execute(
            select(PermissionDo.id, PermissionDo.code).where(
                PermissionDo.code.in_(unique_codes),
                PermissionDo.permission_type == "field",
                PermissionDo.status == "1",
            )
        )
        existing = {code: permission_id for permission_id, code in result.all()}
        missing = [code for code in unique_codes if code not in existing]
        if missing:
            raise ValueError(f"Field permissions do not exist: {missing}")
        return unique_codes

    @staticmethod
    async def _replace_field_permissions(
        mysql, role_id: int, permission_codes: list[str]
    ) -> None:
        codes = await RoleDao._validate_field_permission_codes(mysql, permission_codes)
        await mysql.execute(
            delete(RolePermissionDo).where(RolePermissionDo.role_id == role_id)
        )
        if not codes:
            return
        result = await mysql.execute(
            select(PermissionDo.id).where(PermissionDo.code.in_(codes))
        )
        mysql.add_all(
            [
                RolePermissionDo(role_id=role_id, permission_id=permission_id)
                for permission_id in result.scalars().all()
            ]
        )

    @staticmethod
    async def _ensure_role_code_available(
        mysql, code: str, role_id: int | None = None
    ) -> None:
        """在写入前检查角色编码，避免把可预期冲突暴露为数据库错误。"""
        statement = select(RoleDo.id).where(
            RoleDo.code == code,
            RoleDo.deleted_at.is_(None),
        )
        if role_id is not None:
            statement = statement.where(RoleDo.id != role_id)
        result = await mysql.execute(statement)
        if result.scalar_one_or_none() is not None:
            raise RoleCodeConflictError("角色编码已存在")

    @staticmethod
    async def create_role_by_role_name(
        roles: CreateRoleDto, request: Request
    ) -> RoleDo:
        """创建角色.

        Args:
            roles (CreateRoleDto): 角色信息.
            request (Request): 请求对象.

        Returns:
            RoleDo: 角色对象.
        """
        mysql = request.state.mysql
        role_data = roles.model_dump(
            exclude={"menu_ids", "dept_ids", "field_permission_codes"}
        )
        role_data.setdefault(
            "tenant_id",
            require_tenant_id(request),
        )
        await RoleDao._ensure_role_code_available(mysql, roles.code)
        tenant_id = role_data.get("tenant_id")
        menu_ids = await RoleDao._validate_menu_ids(mysql, roles.menu_ids, tenant_id)
        dept_ids = await RoleDao._validate_dept_ids(mysql, roles.dept_ids, tenant_id)
        role = RoleDo(**role_data)
        mysql.add(role)
        await mysql.flush()
        mysql.add_all(
            [RoleMenuDo(role_id=role.id, menu_id=menu_id) for menu_id in menu_ids]
        )
        mysql.add_all(
            [RoleDeptDo(role_id=role.id, dept_id=dept_id) for dept_id in dept_ids]
        )
        await RoleDao._replace_field_permissions(
            mysql, role.id, roles.field_permission_codes
        )
        return role

    @staticmethod
    async def get_role_by_id(role_id: int, request: Request) -> Union[dict, None]:
        """根据角色ID获取角色信息.

        Args:
            role_id (int): 角色ID.
            request (Request): 请求对象.

        Returns:
            RoleDo: 角色对象.
        """
        mysql = request.state.mysql
        role = await mysql.get(RoleDo, role_id)
        if role is None:
            return None
        tenant_id = current_tenant_id(request)
        if (
            tenant_id is None
            or role.tenant_id != tenant_id
            or role.deleted_at is not None
        ):
            return None
        result = await mysql.execute(
            select(RoleMenuDo.menu_id)
            .where(RoleMenuDo.role_id == role_id)
            .order_by(RoleMenuDo.menu_id)
        )
        dept_result = await mysql.execute(
            select(RoleDeptDo.dept_id)
            .where(RoleDeptDo.role_id == role_id)
            .order_by(RoleDeptDo.dept_id)
        )
        permission_result = await mysql.execute(
            select(PermissionDo.code)
            .join(RolePermissionDo, RolePermissionDo.permission_id == PermissionDo.id)
            .where(
                RolePermissionDo.role_id == role_id,
                PermissionDo.permission_type == "field",
            )
            .order_by(PermissionDo.code)
        )
        return {
            **role.model_dump(),
            "menu_ids": list(result.scalars().all()),
            "dept_ids": list(dept_result.scalars().all()),
            "field_permission_codes": list(permission_result.scalars().all()),
        }

    @staticmethod
    async def get_roles_by_ids(role_ids: list[int], request: Request) -> list[RoleDo]:
        """返回与输入 ID 匹配的角色。"""
        unique_role_ids = list(dict.fromkeys(role_ids))
        if not unique_role_ids:
            return []
        statement = select(RoleDo).where(RoleDo.id.in_(unique_role_ids))
        statement = statement.where(tenant_clause(request, RoleDo))
        statement = statement.where(RoleDo.deleted_at.is_(None))
        result = await request.state.mysql.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def get_role_by_name(role_name: str, request: Request) -> Union[RoleDo, None]:
        """根据角色名称获取角色信息.

        Args:
            role_name (str): 角色名称.
            request (Request): 请求对象.

        Returns:
            RoleDo: 角色对象.
        """
        mysql = request.state.mysql
        stmt = select(RoleDo).where(
            RoleDo.name == role_name,
            tenant_clause(request, RoleDo),
        )
        stmt = stmt.where(tenant_clause(request, RoleDo))
        stmt = stmt.where(RoleDo.deleted_at.is_(None))
        result = await mysql.execute(stmt)
        role = result.scalars().first()
        return role

    @staticmethod
    async def del_role_by_id(role_id: int, request: Request) -> Union[str, None]:
        """根据角色ID删除角色.
        Args:
            role_id (int): 角色ID.
            request (Request): 请求对象.
        """
        mysql = request.state.mysql
        role = await mysql.get(RoleDo, role_id)
        if role is None:
            return "角色不存在"
        tenant_id = current_tenant_id(request)
        if (
            tenant_id is None
            or role.tenant_id != tenant_id
            or role.deleted_at is not None
        ):
            return "角色不存在"
        role.status = "0"
        role.deleted_at = now_utc8_naive()
        role.version = getattr(role, "version", 1) + 1
        role.update_time = now_utc8_naive()
        return None

    @staticmethod
    async def del_role_by_name(role_name: str, request: Request) -> Union[str, None]:
        """根据角色名称删除角色.
        Args:
            role_name (str): 角色名称.
            request (Request): 请求对象.
        """
        mysql = request.state.mysql
        stmt = select(RoleDo).where(
            RoleDo.name == role_name,
            tenant_clause(request, RoleDo),
        )
        result = await mysql.execute(stmt)
        role = result.scalars().first()
        if role is None:
            return "角色不存在"
        tenant_id = current_tenant_id(request)
        if (
            tenant_id is None
            or role.tenant_id != tenant_id
            or role.deleted_at is not None
        ):
            return "角色不存在"
        role.status = "0"
        role.deleted_at = now_utc8_naive()
        role.version = getattr(role, "version", 1) + 1
        role.update_time = now_utc8_naive()
        return None

    @staticmethod
    async def upd_role_by_id(
        roles: UpdataRoleDto, request: Request, role_id: int
    ) -> Union[str, None]:
        """更新角色信息.

        Args:
            roles (UpdataRoleDto): 角色信息.
            request (Request): 请求对象.
            role_id (int): 角色ID.
        Returns:
            RoleDo: 角色对象.
        """
        mysql = request.state.mysql
        role_db: RoleDo = await mysql.get(RoleDo, role_id)
        if role_db is None:
            return "角色不存在"
        tenant_id = current_tenant_id(request)
        if (
            tenant_id is None
            or role_db.tenant_id != tenant_id
            or role_db.deleted_at is not None
        ):
            return "角色不存在"
        role_data = roles.model_dump(exclude_unset=True)
        expected_version = role_data.pop("version", None)
        menu_ids = role_data.pop("menu_ids", None)
        dept_ids = role_data.pop("dept_ids", None)
        field_permission_codes = role_data.pop("field_permission_codes", None)
        if roles.code is not None:
            await RoleDao._ensure_role_code_available(mysql, roles.code, role_id)
        if role_data.get("data_scope") is None:
            role_data.pop("data_scope", None)
        if menu_ids is not None:
            menu_ids = await RoleDao._validate_menu_ids(
                mysql, menu_ids, role_db.tenant_id
            )
            await mysql.execute(delete(RoleMenuDo).where(RoleMenuDo.role_id == role_id))
            mysql.add_all(
                [RoleMenuDo(role_id=role_id, menu_id=menu_id) for menu_id in menu_ids]
            )
        if dept_ids is not None:
            dept_ids = await RoleDao._validate_dept_ids(
                mysql, dept_ids, role_db.tenant_id
            )
            await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role_id))
            mysql.add_all(
                [RoleDeptDo(role_id=role_id, dept_id=dept_id) for dept_id in dept_ids]
            )
        elif role_data.get("data_scope") not in (None, "2"):
            await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role_id))
        if field_permission_codes is not None:
            await RoleDao._replace_field_permissions(
                mysql, role_id, field_permission_codes
            )
        if expected_version is not None and role_db.version != expected_version:
            raise RoleVersionConflictError("角色版本已过期")
        role_data["version"] = RoleDo.version + 1
        role_data["update_time"] = now_utc8_naive()
        result = await mysql.execute(
            update(RoleDo)
            .where(
                RoleDo.id == role_id,
                RoleDo.tenant_id == tenant_id,
                RoleDo.deleted_at.is_(None),
                RoleDo.version == (expected_version or role_db.version),
            )
            .values(**role_data)
        )
        if result.rowcount != 1:
            raise RoleVersionConflictError("角色版本已过期")
        return None

    @staticmethod
    async def batch_update_role_status(
        role_ids: list[int], status: str, request: Request
    ) -> Union[str, None]:
        """批量修改角色状态。"""
        mysql = request.state.mysql
        statement = select(RoleDo).where(RoleDo.id.in_(role_ids))
        statement = statement.where(tenant_clause(request, RoleDo))
        statement = statement.where(RoleDo.deleted_at.is_(None))
        result = await mysql.execute(statement)
        roles = result.scalars().all()
        role_map = {role.id: role for role in roles}
        missing_role_ids = [role_id for role_id in role_ids if role_id not in role_map]
        if missing_role_ids:
            return f"角色不存在: {missing_role_ids}"

        update_time = now_utc8_naive()
        for role in roles:
            role.status = status
            role.version = getattr(role, "version", 1) + 1
            role.update_time = update_time
        return None

    @staticmethod
    async def ger_role_by_all(
        request: Request, name: str, code: str, params: Params
    ) -> Page[RoleListDto]:
        """按角色名称和编码过滤并分页返回角色列表。"""
        mysql = request.state.mysql
        query = select(RoleDo)
        if name:
            query = query.where(RoleDo.name == name)
        if code:
            query = query.where(RoleDo.code == code)
        query = query.where(tenant_clause(request, RoleDo))
        query = query.where(RoleDo.deleted_at.is_(None))
        return await paginate(mysql, query, params=params)
