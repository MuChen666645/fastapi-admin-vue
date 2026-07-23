"""菜单接口控制器。"""

from typing import Annotated, Union

from fastapi import APIRouter, Body, Depends, FastAPI, Path, Query, Request

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.menu_dto import (
    CreateMenuByButtonDto,
    CreateMenubyIframeDto,
    CreateMenuByLinkDto,
    CreateMenuByRouterDto,
    GetMenuDto,
    MenuListDto,
    UpdMenuDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.menu_service import MenuService


class MenuController:
    """菜单接口控制器。"""

    menu = APIRouter(tags=["菜单模块"], prefix="/menu")

    def __init__(self, app: FastAPI):
        """保存应用实例并完成控制器初始化。"""
        self.app = app
        super().__init__()

    @staticmethod
    @menu.post(
        "/add",
        summary="新增菜单",
        dependencies=[Depends(Auth.has_permission("system:menu:add"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_menu(
        request: Request,
        menu: Annotated[
            Union[
                CreateMenuByButtonDto,
                CreateMenuByLinkDto,
                CreateMenubyIframeDto,
                CreateMenuByRouterDto,
            ],
            Body(
                title="新增菜单请求",
                description="根据 menu_type 提交对应菜单请求结构",
                discriminator="menu_type",
            ),
        ],
    ):
        """新增菜单"""
        if menu.menu_type == "C":
            return await MenuService.create_menu_by_router(menu, request)
        elif menu.menu_type == "F":
            return await MenuService.create_menu_by_btn(menu, request)
        elif menu.menu_type == "L":
            return await MenuService.create_menu_by_link(menu, request)
        elif menu.menu_type == "I":
            return await MenuService.create_menu_by_iframe(menu, request)

    @staticmethod
    @menu.get(
        "/list",
        summary="查询菜单列表",
        dependencies=[Depends(Auth.has_permission("system:menu:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[list[MenuListDto]]}},
    )
    async def get_menu_all(
        request: Request,
        menu_name: str = Query(default=None, description="菜单名称"),
        status: str = Query(default=None, pattern="^[01]$", description="菜单状态"),
    ) -> list[MenuListDto]:
        """查询菜单列表"""
        return await MenuService.get_menu_list_all(request, menu_name, status)

    @staticmethod
    @menu.get(
        "/{menu_id}",
        summary="查询菜单详情",
        dependencies=[Depends(Auth.has_permission("system:menu:query"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[GetMenuDto]}},
    )
    async def get_menu_by_id(
        request: Request,
        menu_id: int = Path(description="菜单ID"),
    ):
        """查询菜单详情."""
        return await MenuService.get_menu_by_id_services(menu_id, request)

    @staticmethod
    @menu.put(
        "/{menu_id}",
        summary="修改菜单",
        dependencies=[Depends(Auth.has_permission("system:menu:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def upd_menu_by_id(
        menu: Annotated[
            UpdMenuDto,
            Body(title="修改菜单请求", description="修改菜单请求参数"),
        ],
        request: Request,
        menu_id: int = Path(description="菜单ID"),
    ):
        """修改菜单."""
        return await MenuService.upd_menu_by_id_services(menu_id, menu, request)

    @staticmethod
    @menu.delete(
        "/{menu_id}",
        summary="删除菜单",
        dependencies=[Depends(Auth.has_permission("system:menu:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def del_menu_by_id(
        request: Request,
        menu_id: int = Path(description="菜单ID"),
    ):
        """删除菜单."""
        return await MenuService.del_menu_by_id_services(menu_id, request)
