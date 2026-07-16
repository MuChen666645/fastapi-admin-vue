""" menu service. """

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


class MenuService:
    """menu service."""

    @staticmethod
    def _raise_create_error(result: str | None) -> None:
        if result is not None:
            raise HTTPException(status_code=400, detail=result)

    @staticmethod
    async def create_menu_by_btn(
        menus: CreateMenuByButtonDto, request: Request
    ) -> None:
        """create menu by button."""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_btn(menus, request)
        )

    @staticmethod
    async def create_menu_by_link(menus: CreateMenuByLinkDto, request: Request) -> None:
        """create menu by link."""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_link(menus, request)
        )

    @staticmethod
    async def create_menu_by_iframe(
        menus: CreateMenubyIframeDto, request: Request
    ) -> None:
        """create menu by iframe."""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_iframe(menus, request)
        )

    @staticmethod
    async def create_menu_by_router(
        menus: CreateMenuByRouterDto, request: Request
    ) -> None:
        """create menu by router."""
        MenuService._raise_create_error(
            await MenuDao.create_menu_by_router(menus, request)
        )

    @staticmethod
    async def get_menu_list_all(
        request: Request, menu_name: str, status: str | None = None
    ) -> List[MenuListDto]:
        """get menu list all."""
        menu = await MenuDao.get_menu_list_all(request, menu_name, status)
        return FastApiAdmin.create_three(menu, "menu_id", "parent_id")

    @staticmethod
    async def get_menu_by_id_services(
        menu_id: int, request: Request
    ) -> GetMenuDto:
        """Get menu by id."""
        menu = await MenuDao.get_menu_by_id(menu_id, request)
        if menu is None:
            raise HTTPException(status_code=404, detail="菜单不存在")
        return menu

    @staticmethod
    async def upd_menu_by_id_services(
        menu_id: int, menu: UpdMenuDto, request: Request
    ) -> None:
        """Update menu by id."""
        result = await MenuDao.upd_menu_by_id(menu_id, menu, request)
        if result is not None:
            status_code = 404 if result == "菜单不存在" else 400
            raise HTTPException(status_code=status_code, detail=result)
        return None

    @staticmethod
    async def del_menu_by_id_services(menu_id: int, request: Request) -> None:
        """Delete menu by id."""
        result = await MenuDao.del_menu_by_id(menu_id, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None
