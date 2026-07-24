"""菜单模块物理层."""

from typing import Iterable, List

from fastapi import Request
from sqlalchemy import delete
from sqlmodel import select

from module_admin.dao.tenant_scope import (current_tenant_id,
                                           require_tenant_id, tenant_clause)
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleMenuDo
from module_admin.entity.dto.menu_dto import (CreateMenuByButtonDto,
                                              CreateMenubyIframeDto,
                                              CreateMenuByLinkDto,
                                              CreateMenuByRouterDto,
                                              GetMenuDto, MenuListDto,
                                              UpdMenuDto)
from utils.time_utils import now_utc8_naive


class MenuDao:
    @staticmethod
    def _tenant_filter(request: Request):
        return tenant_clause(request, MenuDo)

    """菜单模块物理层."""

    @staticmethod
    async def _validate_parent(
        mysql,
        menu_id: int | None,
        parent_id: int | None,
        menu_type: str,
        tenant_id: int | None = None,
    ) -> str | None:
        """校验直接父菜单及其祖先层级链。"""
        if menu_type == "F" and not parent_id:
            return "按钮必须绑定父菜单"
        if not parent_id:
            return None
        if menu_id is not None and parent_id == menu_id:
            return "父菜单不能是当前菜单"

        parent = await mysql.get(MenuDo, parent_id)
        if parent is None or tenant_id is None or parent.tenant_id != tenant_id:
            parent = None
        if parent is None:
            return "父菜单不存在"
        if parent.menu_type == "F":
            return "按钮不能作为父菜单"

        visited_ids: set[int] = set()
        current = parent
        while current is not None:
            current_id = current.menu_id
            if current_id in visited_ids:
                return "父菜单层级存在循环"
            if menu_id is not None and current_id == menu_id:
                return "父菜单不能是当前菜单的后代节点"

            visited_ids.add(current_id)
            ancestor_id = current.parent_id
            if not ancestor_id:
                break
            current = await mysql.get(MenuDo, ancestor_id)
            if current is not None and (
                tenant_id is None or current.tenant_id != tenant_id
            ):
                current = None
            if current is None:
                return "父菜单层级不存在"
        return None

    @staticmethod
    async def _upsert_button_permission(mysql, menu: MenuDo) -> None:
        """新增或更新按钮菜单对应的权限目录记录。"""
        if menu.menu_type != "F" or not menu.perms:
            return

        permission_result = await mysql.execute(
            select(PermissionDo).where(PermissionDo.code == menu.perms)
        )
        permission = permission_result.scalars().first()
        permission_data = {
            "name": menu.menu_name,
            "code": menu.perms,
            "module": menu.perms.split(":")[0],
            "permission_type": "button",
            "remark": menu.remark,
            "update_time": now_utc8_naive(),
        }
        if permission is None:
            mysql.add(PermissionDo(status="1", **permission_data))
            return

        permission.sqlmodel_update(permission_data)

    @staticmethod
    async def _delete_permission_if_unused(
        mysql, permission_code: str | None, exclude_menu_ids: Iterable[int] = ()
    ) -> None:
        """当权限标识不再被按钮菜单使用时清理权限目录记录。"""
        if not permission_code or permission_code == "*:*:*":
            return

        exclude_menu_ids = list(exclude_menu_ids)
        menu_query = select(MenuDo.menu_id).where(
            MenuDo.menu_type == "F",
            MenuDo.perms == permission_code,
        )
        if exclude_menu_ids:
            menu_query = menu_query.where(MenuDo.menu_id.notin_(exclude_menu_ids))

        menu_result = await mysql.execute(menu_query.limit(1))
        if menu_result.scalars().first() is not None:
            return

        permission_result = await mysql.execute(
            select(PermissionDo).where(PermissionDo.code == permission_code)
        )
        permission = permission_result.scalars().first()
        if permission is not None:
            await mysql.delete(permission)

    @staticmethod
    async def get_menu_list_all(
        request: Request, menu_name: str, status: str | None = None
    ) -> List[MenuListDto]:
        """获取菜单列表."""
        mysql = request.state.mysql
        stmt = select(MenuDo).where(MenuDao._tenant_filter(request))
        if menu_name:
            stmt = stmt.where(MenuDo.menu_name == menu_name)
        if status is not None:
            stmt = stmt.where(MenuDo.status == status)
        result = await mysql.execute(stmt)
        menu = result.scalars().all()
        return menu

    @staticmethod
    async def _create_menu(menus, request: Request) -> str | None:
        """校验父节点并在同一事务中创建菜单及按钮权限。"""
        mysql = request.state.mysql
        menu_data = menus.model_dump()
        menu_data["tenant_id"] = require_tenant_id(request)
        parent_id = menu_data.get("parent_id") or None
        menu_data["parent_id"] = parent_id

        parent_error = await MenuDao._validate_parent(
            mysql,
            menu_id=None,
            parent_id=parent_id,
            menu_type=menus.menu_type,
            tenant_id=require_tenant_id(request),
        )
        if parent_error is not None:
            return parent_error

        duplicate_result = await mysql.execute(
            select(MenuDo.menu_id)
            .where(
                MenuDo.menu_name == menus.menu_name,
                MenuDao._tenant_filter(request),
            )
            .limit(1)
        )
        if duplicate_result.scalars().first() is not None:
            return "菜单名称已存在"

        menu = MenuDo(**menu_data)
        mysql.add(menu)
        await mysql.flush()
        await MenuDao._upsert_button_permission(mysql, menu)
        return None

    @staticmethod
    async def create_menu_by_btn(
        menus: CreateMenuByButtonDto, request: Request
    ) -> str | None:
        """创建菜单 - 按钮.

        Args:
            menu (CreateMenuByButtonDto): 菜单信息
            response (Response): 响应对象
        """
        return await MenuDao._create_menu(menus, request)

    @staticmethod
    async def create_menu_by_link(
        menus: CreateMenuByLinkDto, request: Request
    ) -> str | None:
        """创建菜单 - 外链.

        Args:
            menu (CreateMenuByLinkDto): 菜单信息
            response (Response): 响应对象
        """
        return await MenuDao._create_menu(menus, request)

    @staticmethod
    async def create_menu_by_iframe(
        menus: CreateMenubyIframeDto, request: Request
    ) -> str | None:
        """创建菜单 - Iframe.

        Args:
            menu (CreateMenubyIframeDto): 菜单信息
            response (Response): 响应对象
        """
        return await MenuDao._create_menu(menus, request)

    @staticmethod
    async def create_menu_by_router(
        menus: CreateMenuByRouterDto, request: Request
    ) -> str | None:
        """创建菜单 - 路由.

        Args:
            menu (CreateMenuByRouterDto): 菜单信息
            response (Response): 响应对象
        """
        return await MenuDao._create_menu(menus, request)

    @staticmethod
    async def get_menu_by_id(menu_id: int, request: Request) -> GetMenuDto | None:
        """获取菜单详情.

        Args:
            menu_id (int): 菜单ID.
            response (Response): 响应对象.
            Returns:
                GetMenuDto: 菜单详情.
        """
        mysql = request.state.mysql
        stmt = select(MenuDo).where(
            MenuDo.menu_id == menu_id,
            MenuDao._tenant_filter(request),
        )
        result = await mysql.execute(stmt)
        menu = result.scalars().first()
        return menu

    @staticmethod
    async def upd_menu_by_id(
        menu_id: int, menu: UpdMenuDto, request: Request
    ) -> str | None:
        """更新菜单.
        Args:
            menu_id (int): 菜单ID.
            menu (UpdMenuDto): 菜单信息.
            response (Response): 响应对象.
        Returns:
            None.
        """
        mysql = request.state.mysql
        menu_db = await mysql.get(MenuDo, menu_id)
        tenant_id = current_tenant_id(request)
        if menu_db is not None and (
            tenant_id is None or menu_db.tenant_id != tenant_id
        ):
            menu_db = None
        if menu_db is None:
            return "菜单不存在"

        old_menu_type = menu_db.menu_type
        old_perms = menu_db.perms
        menu_data = menu.model_dump(exclude_unset=True)
        if "parent_id" in menu_data:
            menu_data["parent_id"] = menu_data["parent_id"] or None
        effective_parent_id = menu_data.get("parent_id", menu_db.parent_id)
        effective_menu_type = menu_data.get("menu_type", menu_db.menu_type)
        parent_error = await MenuDao._validate_parent(
            mysql,
            menu_id=menu_id,
            parent_id=effective_parent_id,
            menu_type=effective_menu_type,
            tenant_id=require_tenant_id(request),
        )
        if parent_error is not None:
            return parent_error

        if effective_menu_type == "F":
            child_result = await mysql.execute(
                select(MenuDo.menu_id)
                .where(
                    MenuDo.parent_id == menu_id,
                    MenuDao._tenant_filter(request),
                )
                .limit(1)
            )
            if child_result.scalars().first() is not None:
                return "存在子菜单的菜单不能修改为按钮"

        menu_data["update_time"] = now_utc8_naive()
        menu_db.sqlmodel_update(menu_data)
        await mysql.flush()

        if menu_db.menu_type == "F":
            await MenuDao._upsert_button_permission(mysql, menu_db)

        if old_menu_type == "F" and (
            menu_db.menu_type != "F" or old_perms != menu_db.perms
        ):
            await MenuDao._delete_permission_if_unused(mysql, old_perms, [menu_id])
        return None

    @staticmethod
    async def del_menu_by_id(menu_id: int, request: Request) -> str | None:
        """根据菜单ID删除菜单."""
        mysql = request.state.mysql
        menu = await mysql.get(MenuDo, menu_id)
        tenant_id = current_tenant_id(request)
        if menu is not None and (tenant_id is None or menu.tenant_id != tenant_id):
            menu = None
        if menu is None:
            return "菜单不存在"

        menu_result = await mysql.execute(
            select(MenuDo).where(MenuDao._tenant_filter(request))
        )
        menus = menu_result.scalars().all()
        children_map: dict[int | None, list[MenuDo]] = {}
        menu_map = {}
        for menu_item in menus:
            menu_map[menu_item.menu_id] = menu_item
            children_map.setdefault(menu_item.parent_id, []).append(menu_item)

        delete_ids = {menu_id}
        pending_ids = [menu_id]
        while pending_ids:
            current_id = pending_ids.pop()
            for child in children_map.get(current_id, []):
                if child.menu_id not in delete_ids:
                    delete_ids.add(child.menu_id)
                    pending_ids.append(child.menu_id)

        delete_id_list = list(delete_ids)
        delete_menus = [menu_map[current_id] for current_id in delete_id_list]
        permission_codes = {
            menu_item.perms
            for menu_item in delete_menus
            if menu_item.menu_type == "F" and menu_item.perms
        }

        await mysql.execute(
            delete(RoleMenuDo).where(RoleMenuDo.menu_id.in_(delete_id_list))
        )
        for permission_code in permission_codes:
            await MenuDao._delete_permission_if_unused(
                mysql, permission_code, exclude_menu_ids=delete_ids
            )
        await mysql.execute(
            delete(MenuDo).where(
                MenuDo.menu_id.in_(delete_id_list),
                MenuDao._tenant_filter(request),
            )
        )
        return None
