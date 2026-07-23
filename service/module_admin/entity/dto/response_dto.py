"""通用响应模型。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

DataT = TypeVar("DataT")


class ApiResponseDto(BaseModel, Generic[DataT]):
    """统一 API 响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    code: int = Field(..., description="响应状态码")
    error_code: str | None = Field(default=None, description="稳定错误码")
    message: str = Field(..., description="响应消息")
    data: DataT | None = Field(default=None, description="响应数据")
