"""系统通知公告模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class NoticeDo(SQLModel, table=True):
    """授权管理用户可见的通知公告。"""

    __tablename__ = "notices"

    id: int | None = Field(title="公告编号", default=None, primary_key=True)
    notice_title: str = Field(title="公告标题", max_length=100, index=True)
    notice_type: str = Field(title="公告类型", default="notice", max_length=20, index=True)
    notice_content: str = Field(
        title="公告内容", sa_column=Column(Text, nullable=False)
    )
    status: str = Field(title="公告状态", default="1", max_length=1, index=True)
    publish_time: datetime | None = Field(title="发布时间", default=None, index=True)
    create_by: int | None = Field(title="创建人", default=None, index=True)
    create_time: datetime = Field(title="创建时间", default_factory=now_utc8_naive)
    update_time: datetime = Field(title="更新时间", default_factory=now_utc8_naive)
