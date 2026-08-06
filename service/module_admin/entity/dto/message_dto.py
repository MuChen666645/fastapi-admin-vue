"""消息中心 API DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from module_admin.entity.message_type import MessageType


class MessageCreateDto(BaseModel):
    """创建消息中心消息。"""

    message_title: str = Field(
        title="消息标题", min_length=1, max_length=100, description="消息标题"
    )
    message_type: MessageType = Field(
        title="消息类型", default=MessageType.SYSTEM, description="消息类型"
    )
    message_content: str = Field(title="消息内容", min_length=1, description="消息内容")
    status: str = Field(
        title="消息状态", default="1", pattern="^[01]$", description="消息状态"
    )
    publish_time: datetime | None = Field(
        title="发布时间", default=None, description="发布时间"
    )
    recipient_user_ids: list[int] = Field(
        default_factory=list,
        description="接收用户ID列表，留空表示当前租户全部有效用户",
    )
    delivery_channels: list[str] = Field(
        default_factory=lambda: ["inbox"],
        description="投递渠道：inbox、webhook、email、sms",
    )

    @field_validator("delivery_channels")
    @classmethod
    def validate_delivery_channels(cls, value: list[str]) -> list[str]:
        """只允许已注册渠道，避免消息配置后静默丢失。"""
        supported = {"inbox", "webhook", "email", "sms"}
        invalid = sorted(set(value) - supported)
        if invalid:
            raise ValueError(f"不支持的消息渠道: {invalid}")
        if not value:
            raise ValueError("至少需要一个消息渠道")
        return list(dict.fromkeys(value))


class MessageUpdateDto(BaseModel):
    """更新消息中心消息。"""

    model_config = ConfigDict(from_attributes=True)

    message_title: str | None = Field(
        title="消息标题",
        default=None,
        min_length=1,
        max_length=100,
        description="消息标题",
    )
    message_type: MessageType | None = Field(
        title="消息类型", default=None, description="消息类型"
    )
    message_content: str | None = Field(
        title="消息内容", default=None, min_length=1, description="消息内容"
    )
    status: str | None = Field(
        title="消息状态", default=None, pattern="^[01]$", description="消息状态"
    )
    publish_time: datetime | None = Field(
        title="发布时间", default=None, description="发布时间"
    )


class MessageDto(BaseModel):
    """管理端消息响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(title="消息编号", description="消息编号")
    message_title: str = Field(title="消息标题", description="消息标题")
    message_type: str = Field(title="消息类型", description="消息类型")
    message_content: str = Field(title="消息内容", description="消息内容")
    status: str = Field(title="消息状态", description="0停用，1正常")
    publish_time: datetime | None = Field(title="发布时间", description="发布时间")
    create_by: int | None = Field(title="创建人", description="创建人")
    create_time: datetime = Field(title="创建时间", description="创建时间")
    update_time: datetime = Field(title="更新时间", description="更新时间")


class MessageItemDto(BaseModel):
    """个人消息中心列表和详情响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="消息编号")
    message_title: str = Field(description="消息标题")
    message_type: str = Field(description="消息类型")
    message_content: str = Field(description="消息内容")
    publish_time: datetime | None = Field(description="发布时间")
    read_at: datetime | None = Field(description="阅读时间")


class MessageLatestDto(BaseModel):
    """消息中心三类最新消息。"""

    system: list[MessageItemDto] = Field(
        default_factory=list, description="最新系统通知，最多5条"
    )
    approval: list[MessageItemDto] = Field(
        default_factory=list, description="最新审批消息，最多5条"
    )
    alarm: list[MessageItemDto] = Field(
        default_factory=list, description="最新报警提醒，最多5条"
    )


class MessageUnreadCountDto(BaseModel):
    """当前用户未读消息数量。"""

    unread_count: int = Field(ge=0, description="未读消息数量")


class MessageReadAllDto(BaseModel):
    """批量标记已读结果。"""

    updated_count: int = Field(ge=0, description="本次标记为已读的消息数量")
