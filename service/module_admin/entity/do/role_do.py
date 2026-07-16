""" Role Domain Object. """

from sqlmodel import SQLModel, Field
from datetime import datetime
from utils.time_utils import now_utc8_naive


class RoleDo(SQLModel, table=True):
    """Role Domain Object."""

    __tablename__ = "roles"
    id: int = Field(primary_key=True, description="角色ID")
    name: str = Field(
        max_length=100, nullable=False, description="角色名称", unique=True
    )
    code: str = Field(max_length=100, nullable=False, description="角色编码")
    description: str = Field(max_length=255, description="角色描述")
    create_time: datetime = Field(
        default_factory=now_utc8_naive, description="创建时间"
    )
    update_time: datetime = Field(
        default_factory=now_utc8_naive, description="更新时间"
    )
    status: str = Field(default="1", max_length=1, description="状态,0禁用,1正常")


class RoleMenuDo(SQLModel, table=True):
    """Role Menu Domain Object."""

    __tablename__ = "role_menu"
    role_id: int = Field(
        foreign_key="roles.id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
        description="角色ID",
    )
    menu_id: int = Field(
        foreign_key="menu.menu_id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
        description="菜单ID",
    )
