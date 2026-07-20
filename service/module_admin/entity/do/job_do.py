"""定时任务及执行日志模型。"""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class ScheduledJobDo(SQLModel, table=True):
    """已持久化的注册任务定义。"""

    __tablename__ = "scheduled_jobs"

    id: int | None = Field(title="任务编号", default=None, primary_key=True)
    job_name: str = Field(title="任务名称", max_length=100, index=True)
    job_key: str = Field(title="任务标识", max_length=100, unique=True, index=True)
    task_name: str = Field(title="处理器名称", max_length=200, index=True)
    cron_expression: str = Field(title="Cron 表达式", max_length=100)
    args_json: str = Field(
        title="任务参数",
        default="{}",
        sa_column=Column(Text, nullable=False),
    )
    status: str = Field(title="任务状态", default="1", max_length=1, index=True)
    last_run_time: datetime | None = Field(title="上次执行时间", default=None)
    next_run_time: datetime | None = Field(title="下次执行时间", default=None)
    last_status: str | None = Field(title="上次执行状态", default=None, max_length=20)
    last_message: str | None = Field(
        title="上次执行消息", default=None, sa_column=Column(Text, nullable=True)
    )
    create_by: int | None = Field(title="创建人", default=None, index=True)
    create_time: datetime = Field(title="创建时间", default_factory=now_utc8_naive)
    update_time: datetime = Field(title="更新时间", default_factory=now_utc8_naive)


class JobLogDo(SQLModel, table=True):
    """一次定时任务执行结果。"""

    __tablename__ = "job_logs"

    id: int | None = Field(title="日志编号", default=None, primary_key=True)
    job_id: int | None = Field(title="任务编号", default=None, index=True)
    task_name: str = Field(title="处理器名称", max_length=200, index=True)
    status: str = Field(title="执行状态", max_length=20, index=True)
    message: str | None = Field(
        title="执行消息", default=None, sa_column=Column(Text, nullable=True)
    )
    start_time: datetime = Field(
        title="开始时间", default_factory=now_utc8_naive, index=True
    )
    end_time: datetime | None = Field(title="结束时间", default=None)
    duration_ms: int | None = Field(title="耗时毫秒数", default=None)
