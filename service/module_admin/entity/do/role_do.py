"""角色及角色授权领域模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class RoleDo(SQLModel, table=True):
    """角色数据库模型。"""

    __tablename__ = "roles"

    id: int = Field(primary_key=True, description="Role ID")
    name: str = Field(max_length=100, nullable=False, unique=True)
    code: str = Field(max_length=100, nullable=False)
    description: str = Field(max_length=255)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)
    status: str = Field(default="1", max_length=1)
    data_scope: str = Field(
        default="5",
        max_length=1,
        description="1 all, 2 custom departments, 3 department, 4 descendants, 5 self",
    )


class RoleMenuDo(SQLModel, table=True):
    """角色与菜单关联模型。"""

    __tablename__ = "role_menu"

    role_id: int = Field(
        foreign_key="roles.id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )
    menu_id: int = Field(
        foreign_key="menu.menu_id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )


class RoleDeptDo(SQLModel, table=True):
    """角色与自定义数据权限部门关联模型。"""

    __tablename__ = "role_dept"

    role_id: int = Field(
        foreign_key="roles.id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )
    dept_id: int = Field(
        foreign_key="departments.dept_id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )
