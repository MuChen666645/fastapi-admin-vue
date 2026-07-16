""" Role DTO. """

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleDto(BaseModel):
    """Role Dto."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(None, max_length=50, description="角色名称")
    code: str | None = Field(None, max_length=50, description="角色编码")
    description: str | None = Field(None, max_length=255, description="角色描述")


class CreateRoleDto(RoleDto):
    """Create Role DTO."""

    model_config = ConfigDict(from_attributes=True)

    menu_ids: list[int] = Field(default_factory=list, description="绑定的菜单ID列表")


class UpdataRoleDto(RoleDto):
    """Update Role DTO."""

    model_config = ConfigDict(from_attributes=True)

    menu_ids: list[int] | None = Field(default=None, description="绑定的菜单ID列表")


class BatchUpdateRoleStatusDto(BaseModel):
    """Batch update role status DTO."""

    model_config = ConfigDict(from_attributes=True)

    role_ids: list[int] = Field(..., min_length=1, description="角色ID列表")
    status: str = Field(..., description="状态,0禁用,1正常")

    @field_validator("status")
    def validator_status(cls, val):
        if val not in {"0", "1"}:
            raise ValueError
        return val


class RoleListDto(RoleDto):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
    status: str = Field(..., description="状态,0禁用,1正常")


class RoleDetailDto(RoleListDto):
    """Role detail DTO."""

    model_config = ConfigDict(from_attributes=True)

    menu_ids: list[int] = Field(default_factory=list, description="绑定的菜单ID列表")
