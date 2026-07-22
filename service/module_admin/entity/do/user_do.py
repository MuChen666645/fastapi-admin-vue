"""用户数据库模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class UserDo(SQLModel, table=True):
    """用户数据库模型。"""

    __tablename__ = "users"
    id: int = Field(primary_key=True, description="用户ID")
    create_time: datetime = Field(
        default_factory=now_utc8_naive,
        description="创建时间",
        allow_mutation=True,
    )
    username: str = Field(
        default=None, description="用户名", nullable=False, max_length=50, unique=True
    )
    password: str = Field(default=None, description="密码", nullable=False)
    password_changed_at: datetime | None = Field(
        default=None, description="密码修改时间"
    )
    must_change_password: bool = Field(
        default=True, description="是否强制首次修改密码"
    )
    email: str | None = Field(default=None, description="邮箱", unique=True)
    phone: str | None = Field(
        default=None, description="手机号", max_length=11, unique=True
    )
    role_id: int | None = Field(
        default=None,
        foreign_key="roles.id",
        ondelete="SET NULL",
        nullable=True,
        description="角色ID",
    )
    tenant_id: int | None = Field(
        default=None,
        foreign_key="tenants.id",
        ondelete="RESTRICT",
        nullable=True,
        index=True,
        description="租户ID",
    )
    auth_provider: str = Field(default="local", max_length=20, nullable=False)
    auth_subject: str | None = Field(default=None, max_length=255, unique=True)
    dept_id: int | None = Field(
        default=None,
        foreign_key="departments.dept_id",
        ondelete="RESTRICT",
        nullable=True,
        index=True,
        description="部门ID",
    )
    nickname: str | None = Field(default=None, description="用户昵称", max_length=50)
    sex: str | None = Field(default=None, description="用户性别,0女,1男")
    avatar: str | None = Field(default=None, description="用户头像")
    update_time: datetime | None = Field(default=None, description="更新时间")
    status: str = Field(default="1", max_length=1, description="状态,0禁用,1正常")
    mfa_enabled: bool = Field(default=False, description="是否启用多因素认证")
    mfa_secret_encrypted: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="加密后的 MFA 密钥",
    )
    mfa_recovery_codes_encrypted: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="加密后的 MFA 恢复码",
    )


class UserPasswordHistoryDo(SQLModel, table=True):
    """用户历史密码记录。"""

    __tablename__ = "user_password_history"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        nullable=False,
        index=True,
    )
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)


class PasswordResetTokenDo(SQLModel, table=True):
    """邮箱或短信密码找回令牌。"""

    __tablename__ = "password_reset_tokens"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        nullable=False,
        index=True,
    )
    channel: str = Field(max_length=10, nullable=False)
    token_hash: str = Field(max_length=64, nullable=False, unique=True, index=True)
    expires_at: datetime = Field(nullable=False, index=True)
    consumed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=now_utc8_naive)


class UserRoleDo(SQLModel, table=True):
    """用户与角色关联模型。"""

    __tablename__ = "user_role"
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        nullable=False,
        description="用户ID",
        primary_key=True,
    )
    role_id: int = Field(
        foreign_key="roles.id",
        ondelete="CASCADE",
        nullable=False,
        description="角色ID",
        primary_key=True,
    )
