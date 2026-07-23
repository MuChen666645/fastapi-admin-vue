"""租户管理请求和响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TenantCreateDto(BaseModel):
    """创建租户请求。"""

    code: str = Field(min_length=1, max_length=64, description="租户编码")
    name: str = Field(min_length=1, max_length=100, description="租户名称")
    description: str | None = Field(
        default=None, max_length=500, description="租户描述"
    )


class TenantUpdateDto(BaseModel):
    """更新租户请求。"""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None, min_length=1, max_length=100, description="租户名称"
    )
    description: str | None = Field(
        default=None, max_length=500, description="租户描述"
    )
    status: str | None = Field(default=None, pattern="^[01]$", description="租户状态")
    version: int = Field(ge=1, description="乐观锁版本号")


class TenantDto(TenantCreateDto):
    """租户响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="租户编号")
    status: str = Field(description="租户状态")
    version: int = Field(description="乐观锁版本号")
    deleted_at: datetime | None = Field(default=None, description="删除时间")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


class TenantMemberAddDto(BaseModel):
    """添加租户成员请求。"""

    user_id: int = Field(gt=0, description="用户编号")
    is_default: bool = Field(default=False, description="是否设为用户默认租户")


class TenantMemberUpdateDto(BaseModel):
    """更新租户成员请求。"""

    status: str = Field(pattern="^[01]$", description="成员状态")
    is_default: bool = Field(default=False, description="是否设为用户默认租户")
    version: int = Field(ge=1, description="乐观锁版本号")


class TenantMemberDto(BaseModel):
    """租户成员响应。"""

    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(description="用户编号")
    tenant_id: int = Field(description="租户编号")
    username: str = Field(description="用户名")
    nickname: str | None = Field(default=None, description="昵称")
    status: str = Field(description="成员状态")
    is_default: bool = Field(description="是否默认租户")
    version: int = Field(description="乐观锁版本号")


class TenantSwitchDto(BaseModel):
    """切换当前租户请求。"""

    tenant_id: int = Field(gt=0, description="目标租户编号")
