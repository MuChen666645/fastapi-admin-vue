"""文件接口响应 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FileMetadataDto(BaseModel):
    """上传或查询文件时返回的元数据。"""

    model_config = ConfigDict(from_attributes=True)

    file_id: str = Field(title="文件标识", description="文件唯一标识，通常为 UUID")
    original_name: str = Field(title="原始文件名", description="文件上传时的原始名称")
    storage_backend: str = Field(title="存储后端", description="文件存储后端")
    content_type: str | None = Field(title="文件类型", description="文件的 MIME 类型")
    file_size: int = Field(title="文件大小", description="文件大小（字节）")
    checksum: str | None = Field(title="文件校验和", description="文件的校验和")
    created_by: int | None = Field(title="上传人", description="上传文件的用户 ID")
    create_time: datetime = Field(title="创建时间", description="文件创建时间")


class FileUploadResultDto(FileMetadataDto):
    """包含下载接口路径的上传结果。"""

    download_url: str = Field(title="文件下载接口路径", description="文件下载接口路径")


class FileChunkInitDto(BaseModel):
    """分片上传初始化参数。"""

    filename: str = Field(min_length=1, max_length=255, description="文件名")
    content_type: str | None = Field(default=None, max_length=255, description="文件类型")
    total_size: int = Field(gt=0, description="文件总大小")
    total_chunks: int = Field(gt=0, le=10000, description="分片总数")


class FileChunkCompleteDto(BaseModel):
    """分片上传完成参数。"""

    upload_id: str = Field(min_length=36, max_length=36, description="上传会话")


class FilePresignedUrlDto(BaseModel):
    """文件临时访问地址。"""

    url: str = Field(description="临时访问地址")
    expires_in: int = Field(description="有效秒数")
