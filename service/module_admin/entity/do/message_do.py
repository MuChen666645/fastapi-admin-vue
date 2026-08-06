"""消息中心数据库模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class MessageDo(SQLModel, table=True):
    """租户范围内可投递给管理用户的消息。"""

    __tablename__ = "messages"

    tenant_id: int | None = Field(default=1, index=True, description="租户ID")

    id: int | None = Field(title="消息编号", default=None, primary_key=True)
    message_title: str = Field(title="消息标题", max_length=100, index=True)
    message_type: str = Field(
        title="消息类型", default="system", max_length=20, index=True
    )
    message_content: str = Field(
        title="消息内容", sa_column=Column(Text, nullable=False)
    )
    status: str = Field(title="消息状态", default="1", max_length=1, index=True)
    publish_time: datetime | None = Field(title="发布时间", default=None, index=True)
    create_by: int | None = Field(title="创建人", default=None, index=True)
    create_time: datetime = Field(title="创建时间", default_factory=now_utc8_naive)
    update_time: datetime = Field(title="更新时间", default_factory=now_utc8_naive)


class MessageRecipientDo(SQLModel, table=True):
    """消息收件人及个人阅读状态。"""

    __tablename__ = "message_recipients"

    message_id: int = Field(
        foreign_key="messages.id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )
    user_id: int = Field(
        foreign_key="users.id",
        ondelete="CASCADE",
        nullable=False,
        primary_key=True,
    )
    delivered_at: datetime = Field(default_factory=now_utc8_naive)
    read_at: datetime | None = Field(default=None, index=True)
