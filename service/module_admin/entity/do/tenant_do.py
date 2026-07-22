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
    status: str = Field(default="1", max_length=1, nullable=False, index=True)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)
