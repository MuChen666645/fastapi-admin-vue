"""异步导出任务模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class ExportTaskDo(SQLModel, table=True):
    """记录异步导出的状态、结果文件和租户归属。"""

    __tablename__ = "export_tasks"

    id: str = Field(primary_key=True, max_length=36)
    tenant_id: int = Field(index=True)
    created_by: int = Field(index=True)
    resource: str = Field(max_length=30, index=True)
    status: str = Field(default="pending", max_length=20, index=True)
    file_id: str | None = Field(default=None, max_length=36, index=True)
    error_message: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
    started_at: datetime | None = Field(default=None)
    finished_at: datetime | None = Field(default=None)
    expires_at: datetime = Field(index=True)
