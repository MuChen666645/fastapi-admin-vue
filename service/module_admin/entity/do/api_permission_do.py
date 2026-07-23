"""API 权限目录模型。"""

from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class ApiPermissionCatalogDo(SQLModel, table=True):
    """从应用路由自动同步的 API 权限目录。"""

    __tablename__ = "api_permission_catalog"
    __table_args__ = (
        UniqueConstraint(
            "api_path",
            "api_method",
            "permission_code",
            name="uq_api_permission_catalog_path_method_code",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    permission_code: str = Field(max_length=100, nullable=False, index=True)
    api_path: str = Field(max_length=255, nullable=False)
    api_method: str = Field(max_length=20, nullable=False)
    route_name: str | None = Field(default=None, max_length=200)
    status: str = Field(default="1", max_length=1, nullable=False, index=True)
    first_seen_at: datetime = Field(default_factory=now_utc8_naive)
    last_seen_at: datetime = Field(default_factory=now_utc8_naive, index=True)
