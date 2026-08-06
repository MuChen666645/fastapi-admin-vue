"""消息中心外部渠道投递记录模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class MessageDeliveryDo(SQLModel, table=True):
    """一次消息渠道投递及重试状态。"""

    __tablename__ = "message_deliveries"

    id: int | None = Field(default=None, primary_key=True)
    tenant_id: int | None = Field(default=1, index=True)
    message_id: int = Field(foreign_key="messages.id", ondelete="CASCADE", index=True)
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE", index=True)
    channel: str = Field(max_length=20, index=True)
    destination: str | None = Field(default=None, max_length=500)
    status: str = Field(default="pending", max_length=20, index=True)
    attempts: int = Field(default=0)
    next_attempt_at: datetime = Field(default_factory=now_utc8_naive, index=True)
    last_error: str | None = Field(default=None, max_length=1000)
    delivered_at: datetime | None = Field(default=None)
    lease_token: str | None = Field(default=None, max_length=64, index=True)
    lease_until: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
    updated_at: datetime = Field(default_factory=now_utc8_naive)
