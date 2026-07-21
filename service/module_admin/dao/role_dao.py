from typing import Union

from fastapi import Request
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import delete, select

from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.organization_do import DepartmentDo
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo, RoleMenuDo
from module_admin.entity.dto.role_dto import (CreateRoleDto, RoleListDto,
                                              UpdataRoleDto)
from utils.time_utils import now_utc8_naive


class RoleDao:
    """持久化角色及其菜单、部门关联记录。"""

    @staticmethod
    async def _validate_dept_ids(mysql, dept_ids: list[int]) -> list[int]:
        """去重部门 ID，并拒绝不存在的部门。"""
        unique_dept_ids = list(dict.fromkeys(dept_ids))
        if not unique_dept_ids:
            return []

        result = await mysql.execute(
            select(DepartmentDo.dept_id).where(
                DepartmentDo.dept_id.in_(unique_dept_ids)
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
    async def _validate_menu_ids(mysql, menu_ids: list[int]) -> list[int]:
        """校验菜单存在性后返回去重的菜单 ID。"""
        unique_menu_ids = list(dict.fromkeys(menu_ids))
        if not unique_menu_ids:
            return []

        result = await mysql.execute(
            select(MenuDo.menu_id).where(MenuDo.menu_id.in_(unique_menu_ids))
        )
        existing_menu_ids = set(result.scalars().all())
        missing_menu_ids = [
            menu_id for menu_id in unique_menu_ids if menu_id not in existing_menu_ids
        ]
        if missing_menu_ids:
            raise ValueError(f"菜单不存在: {missing_menu_ids}")
        return unique_menu_ids

    @staticmethod
    async def create_role_by_role_name(roles: CreateRoleDto, request: Request) -> None:
        """创建角色.

        Args:
            roles (CreateRoleDto): 角色信息.
            request (Request): 请求对象.

        Returns:
            RoleDo: 角色对象.
        """
        mysql = request.state.mysql
        role_data = roles.model_dump(exclude={"menu_ids", "dept_ids"})
        menu_ids = await RoleDao._validate_menu_ids(mysql, roles.menu_ids)
        dept_ids = await RoleDao._validate_dept_ids(mysql, roles.dept_ids)
        role = RoleDo(**role_data)
        mysql.add(role)
        await mysql.flush()
        mysql.add_all(
            [RoleMenuDo(role_id=role.id, menu_id=menu_id) for menu_id in menu_ids]
        )
        mysql.add_all(
            [RoleDeptDo(role_id=role.id, dept_id=dept_id) for dept_id in dept_ids]
        )
        return None

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
        return {
            **role.model_dump(),
            "menu_ids": list(result.scalars().all()),
            "dept_ids": list(dept_result.scalars().all()),
        }

    @staticmethod
    async def get_roles_by_ids(role_ids: list[int], request: Request) -> list[RoleDo]:
        """返回与输入 ID 匹配的角色。"""
        unique_role_ids = list(dict.fromkeys(role_ids))
        if not unique_role_ids:
            return []
        result = await request.state.mysql.execute(
            select(RoleDo).where(RoleDo.id.in_(unique_role_ids))
        )
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
        stmt = select(RoleDo).where(RoleDo.name == role_name)
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
        await mysql.execute(delete(RoleMenuDo).where(RoleMenuDo.role_id == role_id))
        await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role_id))
        await mysql.delete(role)
        return None

    @staticmethod
    async def del_role_by_name(role_name: str, request: Request) -> Union[str, None]:
        """根据角色名称删除角色.
        Args:
            role_name (str): 角色名称.
            request (Request): 请求对象.
        """
        mysql = request.state.mysql
        stmt = select(RoleDo).where(RoleDo.name == role_name)
        result = await mysql.execute(stmt)
        role = result.scalars().first()
        if role is None:
            return "角色不存在"
        await mysql.execute(delete(RoleMenuDo).where(RoleMenuDo.role_id == role.id))
        await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role.id))
        await mysql.delete(role)
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
        role_data = roles.model_dump(exclude_unset=True)
        menu_ids = role_data.pop("menu_ids", None)
        dept_ids = role_data.pop("dept_ids", None)
        if role_data.get("data_scope") is None:
            role_data.pop("data_scope", None)
        if menu_ids is not None:
            menu_ids = await RoleDao._validate_menu_ids(mysql, menu_ids)
            await mysql.execute(
                delete(RoleMenuDo).where(RoleMenuDo.role_id == role_id)
            )
            mysql.add_all(
                [RoleMenuDo(role_id=role_id, menu_id=menu_id) for menu_id in menu_ids]
            )
        if dept_ids is not None:
            dept_ids = await RoleDao._validate_dept_ids(mysql, dept_ids)
            await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role_id))
            mysql.add_all(
                [RoleDeptDo(role_id=role_id, dept_id=dept_id) for dept_id in dept_ids]
            )
        elif role_data.get("data_scope") not in (None, "2"):
            await mysql.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id == role_id))
        role_db.sqlmodel_update(role_data)
        return None

    @staticmethod
    async def batch_update_role_status(
        role_ids: list[int], status: str, request: Request
    ) -> Union[str, None]:
        """批量修改角色状态。"""
        mysql = request.state.mysql
        result = await mysql.execute(select(RoleDo).where(RoleDo.id.in_(role_ids)))
        roles = result.scalars().all()
        role_map = {role.id: role for role in roles}
        missing_role_ids = [role_id for role_id in role_ids if role_id not in role_map]
        if missing_role_ids:
            return f"角色不存在: {missing_role_ids}"

        update_time = now_utc8_naive()
        for role in roles:
            role.status = status
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
        return await paginate(mysql, query, params=params)
