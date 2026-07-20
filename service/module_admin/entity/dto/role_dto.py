"""Role request and response DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleDto(BaseModel):
    """Shared role fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, max_length=50, description="角色名称")
    code: str | None = Field(default=None, max_length=50, description="角色编码")
    description: str | None = Field(default=None, max_length=255, description="角色描述")
    data_scope: str | None = Field(
        default=None,
        pattern="^[1-5]$",
        description="数据权限范围：1全部数据权限，2自定数据权限，3本部门数据权限，4本部门及以下数据权限，5仅本人数据权限",
    )


class CreateRoleDto(RoleDto):
    """Create role DTO."""

    data_scope: str = Field(default="5", pattern="^[1-5]$" , description="数据权限范围")
    menu_ids: list[int] = Field(default_factory=list , description="菜单ID列表")
    dept_ids: list[int] = Field(
        default_factory=list,
        description="自定义数据权限使用的部门列表",
    )


class UpdataRoleDto(RoleDto):
    """Update role DTO."""

    menu_ids: list[int] | None = Field(default=None, description="菜单ID列表")
    data_scope: str | None = Field(default=None, pattern="^[1-5]$", description="数据权限范围")
    dept_ids: list[int] | None = Field(default=None, description="自定义数据权限使用的部门列表")


class BatchUpdateRoleStatusDto(BaseModel):
    """Batch role status DTO."""

    model_config = ConfigDict(from_attributes=True)

    role_ids: list[int] = Field(..., min_length=1 , description="角色ID列表")
    status: str = Field(..., pattern="^[01]$" , description="状态：0停用，1正常")


class RoleListDto(RoleDto):
    """Role list response DTO."""

    id: int = Field(description="角色ID")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    status: str = Field(description="状态：0停用，1正常")
    data_scope: str = Field(default="5", pattern="^[1-5]$", description="数据权限范围")


class RoleDetailDto(RoleListDto):
    """Role detail response DTO."""

    menu_ids: list[int] = Field(default_factory=list, description="菜单ID列表")
    dept_ids: list[int] = Field(default_factory=list, description="自定义数据权限使用的部门列表")
