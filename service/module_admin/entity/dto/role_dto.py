"""Role request and response DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleDto(BaseModel):
    """Shared role fields."""

    model_config = ConfigDict(from_attributes=True)

    name: str | None = Field(default=None, max_length=50)
    code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    data_scope: str | None = Field(
        default=None,
        pattern="^[1-5]$",
        description="1 all, 2 custom departments, 3 department, 4 descendants, 5 self",
    )


class CreateRoleDto(RoleDto):
    """Create role DTO."""

    data_scope: str = Field(default="5", pattern="^[1-5]$")
    menu_ids: list[int] = Field(default_factory=list)
    dept_ids: list[int] = Field(
        default_factory=list,
        description="Departments used by custom data scope",
    )


class UpdataRoleDto(RoleDto):
    """Update role DTO."""

    menu_ids: list[int] | None = Field(default=None)
    data_scope: str | None = Field(default=None, pattern="^[1-5]$")
    dept_ids: list[int] | None = Field(default=None)


class BatchUpdateRoleStatusDto(BaseModel):
    """Batch role status DTO."""

    model_config = ConfigDict(from_attributes=True)

    role_ids: list[int] = Field(..., min_length=1)
    status: str = Field(..., pattern="^[01]$")


class RoleListDto(RoleDto):
    """Role list response DTO."""

    id: int
    create_time: datetime
    update_time: datetime
    status: str
    data_scope: str = Field(default="5", pattern="^[1-5]$")


class RoleDetailDto(RoleListDto):
    """Role detail response DTO."""

    menu_ids: list[int] = Field(default_factory=list)
    dept_ids: list[int] = Field(default_factory=list)
