"""文件元数据模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class FileChunkUploadDo(SQLModel, table=True):
    """分片上传会话及已接收分片状态。"""

    __tablename__ = "file_chunk_uploads"

    upload_id: str = Field(primary_key=True, max_length=36)
    tenant_id: int | None = Field(default=1, index=True)
    created_by: int | None = Field(default=None, index=True)
    original_name: str = Field(max_length=255)
    content_type: str | None = Field(default=None, max_length=255)
    total_size: int = Field(ge=0)
    total_chunks: int = Field(gt=0)
    received_chunks_json: str = Field(
        default="[]",
        sa_column=Column(Text, nullable=False),
    )
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
    updated_at: datetime = Field(default_factory=now_utc8_naive)


class FileMetadataDo(SQLModel, table=True):
    """用于定位和授权已上传文件的元数据。"""

    __tablename__ = "file_metadata"

    tenant_id: int | None = Field(default=1, index=True, description="租户ID")

    file_id: str = Field(title="文件标识", primary_key=True, max_length=36)
    original_name: str = Field(title="原始文件名", max_length=255)
    storage_key: str = Field(title="存储键", max_length=500, unique=True, index=True)
    storage_backend: str = Field(title="存储后端", max_length=20)
    content_type: str | None = Field(title="文件类型", default=None, max_length=255)
    file_size: int = Field(title="文件大小", ge=0)
    checksum: str | None = Field(
        title="文件校验和", default=None, max_length=64, index=True
    )
    created_by: int | None = Field(title="上传人", default=None, index=True)
    create_time: datetime = Field(
        title="创建时间", default_factory=now_utc8_naive, index=True
    )
