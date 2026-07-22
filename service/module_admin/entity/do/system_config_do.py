"""系统参数配置模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class SystemConfigDo(SQLModel, table=True):
    """由管理端维护的键值对系统参数。"""

    __tablename__ = "system_configs"

    tenant_id: int | None = Field(default=None, index=True, description="租户ID")

    id: int | None = Field(title="参数编号", default=None, primary_key=True)
    config_name: str = Field(title="参数名称", max_length=100, index=True)
    config_key: str = Field(title="参数键名", max_length=100, unique=True, index=True)
    config_value: str | None = Field(
        title="参数值",
        default=None,
        sa_column=Column(Text, nullable=True),
    )
    config_type: str = Field(title="参数类型", default="text", max_length=20, index=True)
    is_builtin: bool = Field(title="是否内置", default=False, index=True)
    remark: str | None = Field(title="备注", default=None, max_length=500)
    create_time: datetime = Field(title="创建时间", default_factory=now_utc8_naive)
    update_time: datetime = Field(title="更新时间", default_factory=now_utc8_naive)
