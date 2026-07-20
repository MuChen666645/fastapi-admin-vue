"""系统参数配置 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SystemConfigCreateDto(BaseModel):
    """创建系统参数。"""

    config_name: str = Field(title="参数名称", min_length=1, max_length=100)
    config_key: str = Field(
        title="参数键名",
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z0-9_.:-]*$",
    )
    config_value: str | None = Field(title="参数值", default=None)
    config_type: str = Field(
        title="参数类型", default="text", min_length=1, max_length=20
    )
    is_builtin: bool = Field(title="是否内置", default=False)
    remark: str | None = Field(title="备注", default=None, max_length=500)


class SystemConfigUpdateDto(BaseModel):
    """更新可修改的系统参数字段。"""

    model_config = ConfigDict(from_attributes=True)

    config_name: str | None = Field(
        title="参数名称", default=None, min_length=1, max_length=100
    )
    config_value: str | None = Field(title="参数值", default=None)
    config_type: str | None = Field(
        title="参数类型", default=None, min_length=1, max_length=20
    )
    remark: str | None = Field(title="备注", default=None, max_length=500)


class SystemConfigDto(SystemConfigCreateDto):
    """系统参数响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(title="参数编号")
    create_time: datetime = Field(title="创建时间")
    update_time: datetime = Field(title="更新时间")


class SystemConfigValueDto(BaseModel):
    """参数值查询响应。"""

    config_key: str = Field(title="参数键名")
    config_value: str | None = Field(title="参数值")
