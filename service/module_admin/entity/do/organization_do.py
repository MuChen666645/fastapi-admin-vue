"""部门、岗位及用户岗位关联模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel
from utils.time_utils import now_utc8_naive


class DepartmentDo(SQLModel, table=True):
    __tablename__ = "departments"

    dept_id: int | None = Field(default=None, primary_key=True)
    parent_id: int | None = Field(
        default=None,
        foreign_key="departments.dept_id",
        ondelete="RESTRICT",
        nullable=True,
        index=True,
    )
    ancestors: str = Field(default="", max_length=500)
    dept_name: str = Field(max_length=50, index=True)
    order_num: int = Field(default=0)
    leader: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    status: str = Field(default="1", max_length=1, index=True)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)


class PostDo(SQLModel, table=True):
    __tablename__ = "posts"

    post_id: int | None = Field(default=None, primary_key=True)
    post_code: str = Field(max_length=64, unique=True, index=True)
    post_name: str = Field(max_length=50, index=True)
    post_sort: int = Field(default=0)
    status: str = Field(default="1", max_length=1, index=True)
    remark: str | None = Field(default=None, max_length=500)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)


class UserPostDo(SQLModel, table=True):
    __tablename__ = "user_post"

    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        primary_key=True,
    )
    post_id: int = Field(
        foreign_key="posts.post_id",
        ondelete="RESTRICT",
        primary_key=True,
    )
