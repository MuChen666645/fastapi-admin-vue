"""定时任务管理 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScheduledJobCreateDto(BaseModel):
    """创建持久化定时任务。"""

    job_name: str = Field(title="任务名称", min_length=1, max_length=100)
    job_key: str = Field(
        title="任务标识",
        min_length=1,
        max_length=100,
        pattern=r"^[A-Za-z][A-Za-z0-9_.:-]*$",
    )
    task_name: str = Field(title="处理器名称", min_length=1, max_length=200)
    cron_expression: str = Field(title="Cron 表达式", min_length=9, max_length=100)
    args_json: str = Field(title="任务参数", default="{}", max_length=10000)
    status: str = Field(title="任务状态", default="1", pattern="^[01]$")

    @field_validator("args_json")
    @classmethod
    def validate_args_json(cls, value: str) -> str:
        """校验任务参数必须是合法 JSON。"""
        import json

        json.loads(value)
        return value


class ScheduledJobUpdateDto(BaseModel):
    """更新定时任务。"""

    model_config = ConfigDict(from_attributes=True)

    job_name: str | None = Field(
        title="任务名称", default=None, min_length=1, max_length=100
    )
    task_name: str | None = Field(
        title="处理器名称", default=None, min_length=1, max_length=200
    )
    cron_expression: str | None = Field(
        title="Cron 表达式", default=None, min_length=9, max_length=100
    )
    args_json: str | None = Field(title="任务参数", default=None, max_length=10000)
    status: str | None = Field(title="任务状态", default=None, pattern="^[01]$")

    @field_validator("args_json")
    @classmethod
    def validate_args_json(cls, value: str | None) -> str | None:
        """校验更新参数必须是合法 JSON。"""
        if value is not None:
            import json

            json.loads(value)
        return value


class ScheduledJobDto(ScheduledJobCreateDto):
    """定时任务响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(title="任务编号")
    last_run_time: datetime | None = Field(title="上次执行时间")
    next_run_time: datetime | None = Field(title="下次执行时间")
    last_status: str | None = Field(title="上次执行状态")
    last_message: str | None = Field(title="上次执行消息")
    create_by: int | None = Field(title="创建人")
    create_time: datetime = Field(title="创建时间")
    update_time: datetime = Field(title="更新时间")


class JobRunResultDto(BaseModel):
    """手动执行结果。"""

    job_id: int = Field(title="任务编号")
    status: str = Field(title="执行状态")
    message: str | None = Field(title="执行消息", default=None)
