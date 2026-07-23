"""字典类型和字典数据模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class DictTypeDo(SQLModel, table=True):
    """字典类型。"""

    __tablename__ = "dict_types"

    tenant_id: int | None = Field(default=1, index=True, description="租户ID")

    dict_id: int | None = Field(default=None, primary_key=True)
    dict_name: str = Field(max_length=100, index=True)
    dict_type: str = Field(max_length=100, unique=True, index=True)
    status: str = Field(default="1", max_length=1, index=True)
    remark: str | None = Field(default=None, max_length=500)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)


class DictDataDo(SQLModel, table=True):
    """字典数据。"""

    __tablename__ = "dict_data"

    tenant_id: int | None = Field(default=1, index=True, description="租户ID")

    dict_code: int | None = Field(default=None, primary_key=True)
    dict_sort: int = Field(default=0)
    dict_label: str = Field(max_length=100, index=True)
    dict_value: str = Field(max_length=100)
    dict_type: str = Field(max_length=100, index=True)
    status: str = Field(default="1", max_length=1, index=True)
    remark: str | None = Field(default=None, max_length=500)
    create_time: datetime = Field(default_factory=now_utc8_naive)
    update_time: datetime = Field(default_factory=now_utc8_naive)
