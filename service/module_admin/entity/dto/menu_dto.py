"""菜单请求和响应模型。"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MenuType(str, Enum):
    """菜单类型: F=按钮, L=外链, I=Iframe, C=路由."""

    button: str = "F"
    link: str = "L"
    iframe: str = "I"
    router: str = "C"

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        """为菜单类型枚举补充中文说明和枚举名称元数据。"""
        schema = handler(core_schema)
        schema["description"] = "菜单类型: F=按钮, L=外链, I=Iframe, C=路由"
        schema["x-enum-varnames"] = [item.name for item in cls]
        schema["x-enum-descriptions"] = ["按钮", "外链", "Iframe", "路由"]
        return schema


class CreateMenuByButtonDto(BaseModel):
    """新增按钮菜单请求模型。"""

    model_config = ConfigDict(from_attributes=True, title="新增按钮菜单请求")

    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    parent_id: int = Field(..., title="父菜单ID", description="父菜单ID")
    perms: str = Field(..., title="权限标识", description="权限标识")
    menu_type: Literal["F"] = Field(
        ..., title="菜单类型", description="菜单类型: F=按钮"
    )
    sort: int = Field(..., title="显示排序", description="显示排序")
    remark: str = Field(..., title="备注", description="备注")


class CreateMenuByLinkDto(BaseModel):
    """新增外链菜单请求模型。"""

    model_config = ConfigDict(from_attributes=True, title="新增外链菜单请求")

    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    parent_id: int = Field(..., title="父菜单ID", description="父菜单ID")
    menu_path: str = Field(..., title="菜单链接", description="菜单链接")
    menu_type: Literal["L"] = Field(
        ..., title="菜单类型", description="菜单类型: L=外链"
    )
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    icon: str | None = Field(default=None, title="图标", description="图标")
    remark: str | None = Field(default=None, title="备注", description="备注")


class CreateMenubyIframeDto(BaseModel):
    """新增 Iframe 菜单请求模型。"""

    model_config = ConfigDict(from_attributes=True, title="新增Iframe菜单请求")

    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    parent_id: int = Field(..., title="父菜单ID", description="父菜单ID")
    menu_path: str = Field(..., title="菜单链接", description="菜单链接")
    menu_type: Literal["I"] = Field(
        ..., title="菜单类型", description="菜单类型: I=Iframe"
    )
    component: str = Field(..., title="组件名称", description="组件名称")
    link_url: str | None = Field(default=None, title="链接地址", description="链接地址")
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    is_cache: str = Field(default="0", title="是否缓存", description="是否缓存")
    is_hidden: str = Field(default="0", title="是否隐藏", description="是否隐藏")
    icon: str | None = Field(default=None, title="图标", description="图标")
    remark: str | None = Field(default=None, title="备注", description="备注")


class CreateMenuByRouterDto(BaseModel):
    """新增路由菜单请求模型。"""

    model_config = ConfigDict(from_attributes=True, title="新增路由菜单请求")

    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    parent_id: int = Field(..., title="父菜单ID", description="父菜单ID")
    menu_type: Literal["C"] = Field(
        ..., title="菜单类型", description="菜单类型: C=路由"
    )
    menu_path: str = Field(..., title="菜单链接", description="菜单链接")
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    icon: str | None = Field(default=None, title="图标", description="图标")
    component: str | None = Field(
        default=None, title="组件名称", description="组件名称"
    )
    is_cache: str = Field(default="0", title="是否缓存", description="是否缓存")
    is_hidden: str = Field(default="0", title="是否隐藏", description="是否隐藏")
    remark: str | None = Field(default=None, title="备注", description="备注")


class MenuListChildrenDto(BaseModel):
    """菜单树子节点响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    menu_id: int = Field(..., title="菜单ID", description="菜单ID")
    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    menu_path: str = Field(..., title="菜单链接", description="菜单链接")
    parent_id: int | None = Field(
        default=None, title="父菜单ID", description="父菜单ID"
    )
    perms: str = Field(..., title="权限标识", description="权限标识")
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    menu_type: MenuType = Field(..., title="菜单类型", description="菜单类型")
    link_url: str | None = Field(default=None, title="链接地址", description="链接地址")
    icon: str | None = Field(default=None, title="图标", description="图标")
    component: str | None = Field(
        default=None, title="组件名称", description="组件名称"
    )
    is_cache: str | None = Field(default=None, title="是否缓存", description="是否缓存")
    is_hidden: str | None = Field(
        default=None, title="是否隐藏", description="是否隐藏"
    )
    create_time: datetime = Field(..., title="创建时间", description="创建时间")
    status: str = Field(..., title="状态", description="状态")
    update_time: datetime = Field(..., title="更新时间", description="更新时间")
    remark: str | None = Field(default=None, title="备注", description="备注")


class MenuListDto(MenuListChildrenDto):
    """菜单列表响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    children: list[MenuListChildrenDto] = Field(
        default=[], title="子菜单", description="子菜单"
    )


class UpdMenuDto(BaseModel):
    """修改菜单请求模型。"""

    model_config = ConfigDict(from_attributes=True, title="修改菜单请求")

    menu_name: str | None = Field(
        default=None, title="菜单名称", description="菜单名称"
    )
    parent_id: int | None = Field(
        default=None, title="父菜单ID", description="父菜单ID"
    )
    icon: str | None = Field(default=None, title="图标", description="图标")
    menu_path: str | None = Field(
        default=None, title="菜单链接", description="菜单链接"
    )
    component: str | None = Field(
        default=None, title="组件名称", description="组件名称"
    )
    is_hidden: str | None = Field(
        default=None, title="是否隐藏", description="是否隐藏"
    )
    is_cache: str | None = Field(default=None, title="是否缓存", description="是否缓存")
    menu_type: MenuType | None = Field(
        default=None,
        title="菜单类型",
        description="菜单类型: F=按钮, L=外链, I=Iframe, C=路由",
    )
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    link_url: str | None = Field(default=None, title="链接地址", description="链接地址")
    perms: str | None = Field(default=None, title="权限标识", description="权限标识")
    status: str | None = Field(default=None, title="状态", description="状态")
    remark: str | None = Field(default=None, title="备注", description="备注")


class GetMenuDto(BaseModel):
    """菜单详情响应模型。"""

    model_config = ConfigDict(from_attributes=True, title="菜单详情")

    menu_id: int = Field(..., title="菜单ID", description="菜单ID")
    menu_name: str = Field(..., title="菜单名称", description="菜单名称")
    parent_id: int | None = Field(
        default=None, title="父菜单ID", description="父菜单ID"
    )
    icon: str | None = Field(default=None, title="图标", description="图标")
    menu_path: str | None = Field(
        default=None, title="菜单链接", description="菜单链接"
    )
    component: str | None = Field(
        default=None, title="组件名称", description="组件名称"
    )
    is_hidden: str | None = Field(
        default=None, title="是否隐藏", description="是否隐藏"
    )
    is_cache: str | None = Field(default=None, title="是否缓存", description="是否缓存")
    menu_type: MenuType = Field(..., title="菜单类型", description="菜单类型")
    sort: int | None = Field(default=None, title="显示排序", description="显示排序")
    link_url: str | None = Field(default=None, title="链接地址", description="链接地址")
    perms: str | None = Field(default=None, title="权限标识", description="权限标识")
    status: str = Field(..., title="状态", description="状态")
    create_time: datetime = Field(..., title="创建时间", description="创建时间")
    update_time: datetime = Field(..., title="更新时间", description="更新时间")
    remark: str | None = Field(default=None, title="备注", description="备注")
