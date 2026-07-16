"""部门和岗位请求、响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StatusMixin(BaseModel):
    """包含通用状态的组织请求。"""
    model_config = ConfigDict(from_attributes=True)

    status: str = Field(default="1", description="状态：0停用，1正常")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class DepartmentCreateDto(StatusMixin):
    """新增部门请求。"""

    parent_id: int | None = Field(
        default=None, description="父部门ID，根部门传0或null"
    )
    dept_name: str = Field(max_length=50, description="部门名称")
    order_num: int = Field(default=0, description="显示顺序")
    leader: str | None = Field(default=None, max_length=50, description="负责人")
    phone: str | None = Field(default=None, max_length=20, description="联系电话")
    email: str | None = Field(default=None, max_length=100, description="邮箱")


class DepartmentUpdateDto(BaseModel):
    """修改部门请求。"""
    model_config = ConfigDict(from_attributes=True)

    parent_id: int | None = Field(default=None, description="父部门ID")
    dept_name: str | None = Field(default=None, max_length=50, description="部门名称")
    order_num: int | None = Field(default=None, description="显示顺序")
    leader: str | None = Field(default=None, max_length=50, description="负责人")
    phone: str | None = Field(default=None, max_length=20, description="联系电话")
    email: str | None = Field(default=None, max_length=100, description="邮箱")
    status: str | None = Field(default=None, description="状态：0停用，1正常")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class DepartmentDto(DepartmentCreateDto):
    """部门响应。"""
    dept_id: int
    ancestors: str
    create_time: datetime
    update_time: datetime
    children: list["DepartmentDto"] = Field(default_factory=list)


class PostCreateDto(StatusMixin):
    """新增岗位请求。"""

    post_code: str = Field(max_length=64, description="岗位编码")
    post_name: str = Field(max_length=50, description="岗位名称")
    post_sort: int = Field(default=0, description="岗位排序")
    remark: str | None = Field(default=None, max_length=500, description="备注")


class PostUpdateDto(BaseModel):
    """修改岗位请求。"""
    model_config = ConfigDict(from_attributes=True)

    post_code: str | None = Field(default=None, max_length=64, description="岗位编码")
    post_name: str | None = Field(default=None, max_length=50, description="岗位名称")
    post_sort: int | None = Field(default=None, description="岗位排序")
    status: str | None = Field(default=None, description="状态：0停用，1正常")
    remark: str | None = Field(default=None, max_length=500, description="备注")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in {"0", "1"}:
            raise ValueError("状态只能是0或1")
        return value


class PostDto(PostCreateDto):
    """岗位响应。"""
    post_id: int
    create_time: datetime
    update_time: datetime
