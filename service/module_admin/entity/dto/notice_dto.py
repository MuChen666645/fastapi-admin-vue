"""通知公告 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoticeCreateDto(BaseModel):
    """创建通知公告。"""

    notice_title: str = Field(title="公告标题", min_length=1, max_length=100, description="公告标题")
    notice_type: str = Field(
        title="公告类型", default="notice", min_length=1, max_length=20, description="公告类型"
    )
    notice_content: str = Field(title="公告内容", min_length=1, description="公告内容")
    status: str = Field(title="公告状态", default="1", pattern="^[01]$", description="公告状态")
    publish_time: datetime | None = Field(title="发布时间", default=None, description="发布时间")


class NoticeUpdateDto(BaseModel):
    """更新通知公告。"""

    model_config = ConfigDict(from_attributes=True)

    notice_title: str | None = Field(
        title="公告标题", default=None, min_length=1, max_length=100, description="公告标题"
    )
    notice_type: str | None = Field(
        title="公告类型", default=None, min_length=1, max_length=20, description="公告类型"
    )
    notice_content: str | None = Field(title="公告内容", default=None, min_length=1, description="公告内容")
    status: str | None = Field(title="公告状态", default=None, pattern="^[01]$", description="公告状态")
    publish_time: datetime | None = Field(title="发布时间", default=None, description="发布时间")


class NoticeDto(NoticeCreateDto):
    """通知公告响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(title="公告编号", description="公告编号")
    create_by: int | None = Field(title="创建人", description="创建人")
    create_time: datetime = Field(title="创建时间", description="创建时间")
    update_time: datetime = Field(title="更新时间", description="更新时间")
