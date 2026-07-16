"""Common response DTO."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


DataT = TypeVar("DataT")


class ApiResponseDto(BaseModel, Generic[DataT]):
    """Unified API response DTO."""

    model_config = ConfigDict(from_attributes=True)

    code: int = Field(..., description="响应状态码")
    message: str = Field(..., description="响应消息")
    data: DataT | None = Field(default=None, description="响应数据")
