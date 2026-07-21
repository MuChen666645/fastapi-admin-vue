"""菜单业务服务。"""

from fastapi import HTTPException, Request
from module_admin.dao.menu_dao import MenuDao
from module_admin.entity.dto.menu_dto import (
    CreateMenuByButtonDto,
    CreateMenuByLinkDto,
    CreateMenubyIframeDto,
    CreateMenuByRouterDto,
    GetMenuDto,
    UpdMenuDto,
)
from utils.fastapi_admin import FastApiAdmin
from typing import List
from module_admin.entity.dto.menu_dto import MenuListDto
from module_admin.auth.authorization import Auth


class MenuService:
    """处理菜单 CRUD、菜单树和按钮权限同步。"""

    # 非超级管理员不能通过按钮菜单写入或扩大有效权限。
    BUTTON_PERMISSION_MUTATION_MESSAGE = (
        "Only super administrators can modify button permissions"
    )

    @staticmethod
    async def _ensure_button_permission_scope(
        request: Request,
        current_menu_type: str | None = None,
        requested_menu_type: str | None = None,
    ) -> None:
        """确保按钮权限定义只能由超级管理员维护。"""
        actor_roles = await Auth.get_actor_roles(request)
        if Auth.has_admin_role(actor_roles):
            return
        if current_menu_type == "F" or requested_menu_type == "F":
            raise HTTPException(
                status_code=403,
                detail=MenuService.BUTTON_PERMISSION_MUTATION_MESSAGE,
            )

    @staticmethod
    def _raise_create_error(result: str | None) -> None:
        """将菜单 DAO 创建错误转换为面向客户端的 HTTP 异常。"""
        if result is not None:
            raise HTTPException(status_code=400, detail=result)

    @staticmethod
    async def create_menu_by_btn(
        menus: CreateMenuByButtonDto, request: Request
    ) -> None:
        """创建按钮菜单。"""
        await MenuService._ensure_button_permission_scope(
            request,
            requested_menu_type=menus.menu_type,
        )
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_btn(menus, request)
        )

    @staticmethod
    async def create_menu_by_link(menus: CreateMenuByLinkDto, request: Request) -> None:
        """创建外链菜单。"""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_link(menus, request)
        )

    @staticmethod
    async def create_menu_by_iframe(
        menus: CreateMenubyIframeDto, request: Request
    ) -> None:
        """创建 Iframe 菜单。"""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_iframe(menus, request)
        )

    @staticmethod
    async def create_menu_by_router(
        menus: CreateMenuByRouterDto, request: Request
    ) -> None:
        """创建路由菜单。"""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_router(menus, request)
        )

    @staticmethod
    async def get_menu_list_all(
        request: Request, menu_name: str, status: str | None = None
    ) -> List[MenuListDto]:
        """查询全部菜单并组装菜单树。"""
        menu = await MenuDao.get_menu_list_all(request, menu_name, status)
        return FastApiAdmin.create_three(menu, "menu_id", "parent_id")

    @staticmethod
    async def get_menu_by_id_services(
        menu_id: int, request: Request
    ) -> GetMenuDto:
        """按 ID 查询菜单详情。"""
        menu = await MenuDao.get_menu_by_id(menu_id, request)
        if menu is None:
            raise HTTPException(status_code=404, detail="菜单不存在")
        return menu

    @staticmethod
    async def upd_menu_by_id_services(
        menu_id: int, menu: UpdMenuDto, request: Request
    ) -> None:
        """按 ID 修改菜单。"""
        current_menu = await MenuDao.get_menu_by_id(menu_id, request)
        if current_menu is not None:
            await MenuService._ensure_button_permission_scope(
                request,
                current_menu_type=current_menu.menu_type,
                requested_menu_type=menu.menu_type,
            )
        result = await MenuDao.upd_menu_by_id(menu_id, menu, request)
        if result is not None:
            status_code = 404 if result == "菜单不存在" else 400
            raise HTTPException(status_code=status_code, detail=result)
        return None

    @staticmethod
    async def del_menu_by_id_services(menu_id: int, request: Request) -> None:
        """按 ID 删除菜单。"""
        current_menu = await MenuDao.get_menu_by_id(menu_id, request)
        if current_menu is not None:
            await MenuService._ensure_button_permission_scope(
                request,
                current_menu_type=current_menu.menu_type,
            )
        result = await MenuDao.del_menu_by_id(menu_id, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None
