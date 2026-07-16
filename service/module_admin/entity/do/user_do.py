"""User Do Model"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from utils.time_utils import now_utc8_naive


class UserDo(SQLModel, table=True):
    """User Do Model."""

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


class UserRoleDo(SQLModel, table=True):
    """User and Role Do Model."""

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
