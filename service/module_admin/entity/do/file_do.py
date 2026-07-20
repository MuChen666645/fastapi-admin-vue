"""文件元数据模型。"""

from datetime import datetime

from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class FileMetadataDo(SQLModel, table=True):
    """用于定位和授权已上传文件的元数据。"""

    __tablename__ = "file_metadata"

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
