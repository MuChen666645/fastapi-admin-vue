""" User Dto."""

from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator


class BaseLoginRequestDto(BaseModel):
    """Base login request DTO with common fields."""

    model_config = ConfigDict(from_attributes=True)

    captcha_id: str = Field(
        min_length=16,
        max_length=128,
        description="验证码ID",
    )
    captcha: str = Field(description="验证码")


class LoginUserRequestByUsernameDto(BaseLoginRequestDto):
    """Login user request DTO using username."""

    model_config = ConfigDict(from_attributes=True)

    username: str = Field(description="用户名")
    password: str = Field(description="密码")


class LoginUserRequestByPhoneDto(BaseLoginRequestDto):
    """Login user request DTO using phone."""

    model_config = ConfigDict(from_attributes=True)

    phone: str = Field(description="手机号")
    password: str = Field(description="密码")


class RegisterUserRequestDto(BaseModel):
    """Register user request dto."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr | None = Field(default=None, description="邮箱")
    avatar: str | None = Field(default=None, description="头像")
    phone: str = Field(description="手机号")
    nickname: str | None = Field(default=None, description="昵称")
    sex: str | None = Field(default=None, description="性别, 男1,女0")
    password: str = Field(description="密码")

    @field_validator("phone")
    def validator_phone(cls, val):
        if not re.match(r"^1[3-9]\d{9}$", val):
            raise ValueError
        return val


class RegisterUserRequestByUsernameDto(RegisterUserRequestDto):
    """Register user request dto."""

    model_config = ConfigDict(from_attributes=True)

    dept_id: int | None = Field(default=None, description="部门ID")
    post_ids: list[int] = Field(default_factory=list, description="岗位ID列表")

    username: str = Field(description="用户名")


class UpdateUserRequestDto(BaseModel):
    """Update user request dto."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    dept_id: int | None = Field(default=None, description="部门ID")
    post_ids: list[int] | None = Field(default=None, description="岗位ID列表")

    username: str | None = Field(default=None, max_length=50, description="用户名")
    email: EmailStr | None = Field(default=None, description="邮箱")
    phone: str | None = Field(default=None, description="手机号")
    nickname: str | None = Field(default=None, max_length=50, description="昵称")
    sex: str | None = Field(default=None, description="性别, 男1,女0")
    avatar: str | None = Field(default=None, description="头像")
    status: str | None = Field(default=None, description="状态,0禁用,1正常")

    @field_validator("phone")
    def validator_phone(cls, val):
        if val is not None and not re.match(r"^1[3-9]\d{9}$", val):
            raise ValueError
        return val

    @field_validator("sex")
    def validator_sex(cls, val):
        if val is not None and val not in {"0", "1"}:
            raise ValueError
        return val

    @field_validator("status")
    def validator_status(cls, val):
        if val is not None and val not in {"0", "1"}:
            raise ValueError
        return val


class UpdateUserPasswordRequestDto(BaseModel):
    """Update user password request dto."""

    model_config = ConfigDict(from_attributes=True)

    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码")

    @field_validator("old_password", "new_password")
    def validator_password(cls, val):
        if not val or not val.strip():
            raise ValueError
        return val


class BatchUserIdsDto(BaseModel):
    """Batch user operation request DTO."""

    model_config = ConfigDict(from_attributes=True)

    user_ids: list[int] = Field(..., min_length=1, description="用户ID列表")


class BatchUpdateUserStatusDto(BatchUserIdsDto):
    """Batch update user status request DTO."""

    status: str = Field(..., description="状态,0禁用,1正常")

    @field_validator("status")
    def validator_status(cls, val):
        if val not in {"0", "1"}:
            raise ValueError
        return val


class BindUserRolesDto(BaseModel):
    """Bind roles to a user request DTO."""

    model_config = ConfigDict(from_attributes=True)

    role_ids: list[int] = Field(default_factory=list, description="角色ID列表")


class TokenDto(BaseModel):
    """Token DTO."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str | None = Field(default=None, description="访问令牌")


class ResponseUserInfoDto(BaseModel):
    """Response user DTO."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    nickname: str = Field(description="昵称")
    email: str = Field(description="邮箱")
    phone: str = Field(description="手机号")
    sex: str = Field(description="性别")
    avatar: str = Field(description="头像")
    status: int = Field(description="状态")
    created_at: str = Field(description="创建时间")
    updated_at: str = Field(description="更新时间")
    roles: list[str] = Field(description="角色")
    permissions: list[str] = Field(description="权限")


class UserInfoUserDto(BaseModel):
    """User info response user data."""

    model_config = ConfigDict(from_attributes=True)

    dept_id: int | None = Field(default=None, description="部门ID")

    id: int = Field(description="用户ID")
    create_time: datetime = Field(description="创建时间")
    username: str = Field(description="用户名")
    email: str | None = Field(default=None, description="邮箱")
    phone: str | None = Field(default=None, description="手机号")
    role_id: int | None = Field(default=None, description="角色ID")
    nickname: str | None = Field(default=None, description="昵称")
    sex: str | None = Field(default=None, description="性别")
    avatar: str | None = Field(default=None, description="头像")
    update_time: datetime | None = Field(default=None, description="更新时间")
    status: str = Field(description="状态")


class UserInfoRoleDto(BaseModel):
    """User info response role data."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="角色ID")
    name: str = Field(description="角色名称")
    code: str = Field(description="角色编码")
    description: str = Field(description="角色描述")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    status: str = Field(description="状态")


class UserInfoDto(BaseModel):
    """User info response DTO."""

    model_config = ConfigDict(from_attributes=True)

    posts: list[dict] = Field(default_factory=list, description="岗位列表")

    user: UserInfoUserDto = Field(description="用户信息")
    roles: list[UserInfoRoleDto] = Field(description="角色列表")
    permissions: list[str] = Field(description="权限标识列表")


class UserRouteMetaDto(BaseModel):
    """Current user frontend route meta."""

    title: str = Field(description="菜单标题")
    icon: str | None = Field(default=None, description="菜单图标")
    noCache: bool = Field(default=True, description="是否不缓存")
    link: str | None = Field(default=None, description="外链地址")


class UserRouteDto(BaseModel):
    """Current user frontend route menu."""

    path: str = Field(description="路由路径")
    name: str = Field(description="路由名称")
    component: str | None = Field(default=None, description="前端组件路径")
    redirect: str | None = Field(default=None, description="重定向地址")
    hidden: bool = Field(default=False, description="是否隐藏")
    meta: UserRouteMetaDto = Field(description="路由元信息")
    children: list["UserRouteDto"] = Field(default_factory=list, description="子路由")
