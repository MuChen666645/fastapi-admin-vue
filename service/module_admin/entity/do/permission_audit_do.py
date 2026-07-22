"""权限变更版本审计模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class PermissionChangeVersionDo(SQLModel, table=True):
    """角色、菜单和字段权限变更的不可变版本记录。"""

    __tablename__ = "permission_change_versions"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int | None = Field(default=None, index=True)
    actor_user_id: int | None = Field(default=None, index=True)
    resource_type: str = Field(max_length=50, nullable=False, index=True)
    resource_id: str = Field(max_length=100, nullable=False)
    version: int = Field(nullable=False)
    action: str = Field(max_length=30, nullable=False)
    before_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    after_json: str | None = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
