"""权限领域模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel
from utils.time_utils import now_utc8_naive


class PermissionDo(SQLModel, table=True):
    """权限目录表。"""

    __tablename__ = "permissions"

    id: int | None = Field(default=None, primary_key=True, description="权限ID")
    name: str = Field(max_length=100, nullable=False, description="权限名称")
    code: str = Field(
        max_length=100, nullable=False, unique=True, index=True, description="权限编码"
    )
    module: str | None = Field(default=None, max_length=50, description="所属模块")
    permission_type: str = Field(
        default="button", max_length=20, nullable=False, description="权限类型"
    )
    api_path: str | None = Field(default=None, max_length=200, description="接口路径")
    api_method: str | None = Field(default=None, max_length=20, description="请求方法")
    status: str = Field(
        default="1", max_length=1, nullable=False, description="状态:0禁用,1正常"
    )
    create_time: datetime = Field(
        default_factory=now_utc8_naive, description="创建时间"
    )
    update_time: datetime = Field(
        default_factory=now_utc8_naive, description="更新时间"
    )
    remark: str | None = Field(default=None, max_length=500, description="备注")
