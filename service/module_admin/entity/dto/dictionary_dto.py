"""字典模块请求、响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DictStatusDto(BaseModel):
    """包含通用状态的字典请求。"""

    model_config = ConfigDict(from_attributes=True)

    status: str = Field(default="1", description="状态：0停用，1正常")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        """仅允许数据库约定的启用和停用状态值。"""
        if value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class DictTypeCreateDto(DictStatusDto):
    """新增字典类型请求。"""

    dict_name: str = Field(max_length=100, description="字典名称")
    dict_type: str = Field(max_length=100, description="字典类型编码")
    remark: str | None = Field(default=None, max_length=500, description="备注")


class DictTypeUpdateDto(BaseModel):
    """修改字典类型请求。"""

    model_config = ConfigDict(from_attributes=True)

    dict_name: str | None = Field(default=None, max_length=100, description="字典名称")
    dict_type: str | None = Field(
        default=None, max_length=100, description="字典类型编码"
    )
    status: str | None = Field(default=None, description="状态：0停用，1正常")
    remark: str | None = Field(default=None, max_length=500, description="备注")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """校验字典类型部分更新中的可选状态值。"""
        if value is not None and value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class DictTypeDto(DictTypeCreateDto):
    """字典类型响应。"""

    dict_id: int = Field(description="字典类型ID")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")


class DictDataCreateDto(DictStatusDto):
    """新增字典数据请求。"""

    dict_sort: int = Field(default=0, description="字典排序")
    dict_label: str = Field(max_length=100, description="字典标签")
    dict_value: str = Field(max_length=100, description="字典键值")
    dict_type: str = Field(max_length=100, description="字典类型编码")
    remark: str | None = Field(default=None, max_length=500, description="备注")


class DictDataUpdateDto(BaseModel):
    """修改字典数据请求。"""

    model_config = ConfigDict(from_attributes=True)

    dict_sort: int | None = Field(default=None, description="字典排序")
    dict_label: str | None = Field(default=None, max_length=100, description="字典标签")
    dict_value: str | None = Field(default=None, max_length=100, description="字典键值")
    dict_type: str | None = Field(
        default=None, max_length=100, description="字典类型编码"
    )
    status: str | None = Field(default=None, description="状态：0停用，1正常")
    remark: str | None = Field(default=None, max_length=500, description="备注")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """校验字典数据部分更新中的可选状态值。"""
        if value is not None and value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class DictDataDto(DictDataCreateDto):
    """字典数据响应。"""

    dict_code: int = Field(description="字典数据ID")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
