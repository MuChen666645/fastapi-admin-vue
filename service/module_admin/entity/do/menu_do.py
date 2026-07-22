""" 菜单模型."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class MenuDo(SQLModel, table=True):
    """菜单模型."""

    __tablename__ = "menu"

    tenant_id: int | None = Field(default=None, index=True, description="租户ID")
    menu_id: int = Field(primary_key=True, description="菜单ID")
    parent_id: int | None = Field(
        default=None,
        foreign_key="menu.menu_id",
        ondelete="CASCADE",
        nullable=True,
        description="父菜单ID",
    )
    menu_name: str = Field(
        nullable=False, unique=True, max_length=50, description="菜单名称"
    )
    icon: str | None = Field(default=None, nullable=True, description="菜单图标")
    menu_path: str | None = Field(
        default=None, nullable=True, max_length=200, description="菜单路径"
    )
    component: str | None = Field(
        default=None, nullable=True, max_length=200, description="菜单组件"
    )
    is_hidden: str | None = Field(
        default="0", nullable=False, max_length=1, description="是否隐藏(1:是,0:否)"
    )
    is_cache: str | None = Field(
        default="0", nullable=False, max_length=1, description="是否缓存(1:是,0:否)"
    )
    menu_type: str = Field(
        default="C",
        nullable=False,
        max_length=1,
        description="菜单类型(C:菜单,W:外链,I:Iframe,F:按钮)",
    )
    sort: int | None = Field(default=None, nullable=True, description="菜单排序")
    link_url: str | None = Field(
        default=None, nullable=True, max_length=200, description="外链地址"
    )
    perms: str | None = Field(
        default=None, nullable=True, max_length=100, description="权限标识"
    )
    status: str = Field(
        default="1", nullable=False, max_length=1, description="菜单状态(1:启用,0:禁用)"
    )
    create_time: datetime = Field(
        default_factory=now_utc8_naive, nullable=False, description="创建时间"
    )
    update_time: datetime = Field(
        default_factory=now_utc8_naive, nullable=False, description="更新时间"
    )
    remark: str | None = Field(
        default=None, nullable=True, max_length=500, description="备注"
    )
