"""租户领域模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class TenantDo(SQLModel, table=True):
    """租户基础信息。"""

    __tablename__ = "tenants"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=64, nullable=False, unique=True, index=True)
    name: str = Field(max_length=100, nullable=False)
    description: str | None = Field(default=None, max_length=500)
    status: str = Field(default="1", max_length=1, nullable=False, index=True)
    version: int = Field(default=1, nullable=False)
    deleted_at: datetime | None = Field(default=None, index=True)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)


class TenantMemberDo(SQLModel, table=True):
    """用户与租户的有效成员关系。"""

    __tablename__ = "tenant_members"

    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        primary_key=True,
        nullable=False,
    )
    tenant_id: int = Field(
        foreign_key="tenants.id",
        ondelete="CASCADE",
        primary_key=True,
        nullable=False,
        index=True,
    )
    status: str = Field(default="1", max_length=1, nullable=False, index=True)
    is_default: bool = Field(default=False, nullable=False)
    version: int = Field(default=1, nullable=False)
    deleted_at: datetime | None = Field(default=None, index=True)
    joined_at: datetime = Field(default_factory=now_utc8_naive)
    updated_at: datetime = Field(default_factory=now_utc8_naive)
