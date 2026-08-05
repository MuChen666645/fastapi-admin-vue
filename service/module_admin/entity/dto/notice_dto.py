"""通知公告 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from module_admin.entity.notice_type import NoticeType


class NoticeCreateDto(BaseModel):
    """创建通知公告。"""

    notice_title: str = Field(
        title="公告标题", min_length=1, max_length=100, description="公告标题"
    )
    notice_type: NoticeType = Field(
        title="公告类型",
        default=NoticeType.SYSTEM,
        description="公告类型",
    )
    notice_content: str = Field(title="公告内容", min_length=1, description="公告内容")
    status: str = Field(
        title="公告状态", default="1", pattern="^[01]$", description="公告状态"
    )
    publish_time: datetime | None = Field(
        title="发布时间", default=None, description="发布时间"
    )
    recipient_user_ids: list[int] = Field(
        default_factory=list,
        description="收件人用户ID列表，留空表示全体租户用户",
    )
    delivery_channels: list[str] = Field(
        default_factory=lambda: ["inbox"],
        description="投递渠道：inbox、webhook、email、sms",
    )

    @field_validator("delivery_channels")
    @classmethod
    def validate_delivery_channels(cls, value: list[str]) -> list[str]:
        """只允许已经注册的投递渠道，避免配置后静默丢弃通知。"""
        supported = {"inbox", "webhook", "email", "sms"}
        invalid = sorted(set(value) - supported)
        if invalid:
            raise ValueError(f"不支持的通知渠道: {invalid}")
        if not value:
            raise ValueError("至少需要一个通知渠道")
        return list(dict.fromkeys(value))


class NoticeUpdateDto(BaseModel):
    """更新通知公告。"""

    model_config = ConfigDict(from_attributes=True)

    notice_title: str | None = Field(
        title="公告标题",
        default=None,
        min_length=1,
        max_length=100,
        description="公告标题",
    )
    notice_type: NoticeType | None = Field(
        title="公告类型",
        default=None,
        description="公告类型",
    )
    notice_content: str | None = Field(
        title="公告内容", default=None, min_length=1, description="公告内容"
    )
    status: str | None = Field(
        title="公告状态", default=None, pattern="^[01]$", description="公告状态"
    )
    publish_time: datetime | None = Field(
        title="发布时间", default=None, description="发布时间"
    )


class NoticeDto(NoticeCreateDto):
    """通知公告响应。"""

    model_config = ConfigDict(from_attributes=True)

    # 响应保留字符串类型，确保历史自定义类型仍可被管理员查看；新建和修改只接受 NoticeType。
    notice_type: str = Field(title="公告类型", description="公告类型")
    id: int = Field(title="公告编号", description="公告编号")
    create_by: int | None = Field(title="创建人", description="创建人")
    create_time: datetime = Field(title="创建时间", description="创建时间")
    update_time: datetime = Field(title="更新时间", description="更新时间")


class NoticeInboxDto(BaseModel):
    """当前用户收件箱通知。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="公告编号")
    notice_title: str = Field(description="公告标题")
    notice_type: str = Field(description="公告类型")
    notice_content: str = Field(description="公告内容")
    publish_time: datetime | None = Field(description="发布时间")
    read_at: datetime | None = Field(description="阅读时间")


class NoticeLatestDto(BaseModel):
    """消息中心三类最新通知。"""

    system: list[NoticeInboxDto] = Field(
        default_factory=list, description="最新系统通知，最多 5 条"
    )
    approval: list[NoticeInboxDto] = Field(
        default_factory=list, description="最新审批消息，最多 5 条"
    )
    alarm: list[NoticeInboxDto] = Field(
        default_factory=list, description="最新报警提醒，最多 5 条"
    )
