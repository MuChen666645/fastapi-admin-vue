"""角色请求和响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleDto(BaseModel):
    """角色请求共用字段。"""

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
    """新增角色请求模型。"""

    data_scope: str = Field(default="5", pattern="^[1-5]$" , description="数据权限范围")
    menu_ids: list[int] = Field(default_factory=list , description="菜单ID列表")
    dept_ids: list[int] = Field(
        default_factory=list,
        description="自定义数据权限使用的部门列表",
    )


class UpdataRoleDto(RoleDto):
    """修改角色请求模型。"""

    menu_ids: list[int] | None = Field(default=None, description="菜单ID列表")
    data_scope: str | None = Field(default=None, pattern="^[1-5]$", description="数据权限范围")
    dept_ids: list[int] | None = Field(default=None, description="自定义数据权限使用的部门列表")


class BatchUpdateRoleStatusDto(BaseModel):
    """批量修改角色状态请求模型。"""

    model_config = ConfigDict(from_attributes=True)

    role_ids: list[int] = Field(..., min_length=1 , description="角色ID列表")
    status: str = Field(..., pattern="^[01]$" , description="状态：0停用，1正常")


class RoleListDto(RoleDto):
    """角色列表响应模型。"""

    id: int = Field(description="角色ID")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    status: str = Field(description="状态：0停用，1正常")
    data_scope: str = Field(default="5", pattern="^[1-5]$", description="数据权限范围")


class RoleDetailDto(RoleListDto):
    """角色详情响应模型。"""

    menu_ids: list[int] = Field(default_factory=list, description="菜单ID列表")
    dept_ids: list[int] = Field(default_factory=list, description="自定义数据权限使用的部门列表")
