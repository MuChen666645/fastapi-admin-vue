"""Persistent system log models."""

from datetime import datetime

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel
from utils.time_utils import now_utc8_naive


class LoginLogDo(SQLModel, table=True):
    """A login attempt, whether successful or not."""

    __tablename__ = "login_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        ondelete="SET NULL",
        nullable=True,
        index=True,
    )
    username: str = Field(max_length=50, index=True)
    ip_address: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=500)
    status: str = Field(max_length=1, index=True, description="0 failed, 1 successful")
    message: str | None = Field(default=None, max_length=500)
    login_time: datetime = Field(default_factory=now_utc8_naive, index=True)


class OperationLogDo(SQLModel, table=True):
    """An authenticated API operation."""

    __tablename__ = "operation_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        ondelete="SET NULL",
        nullable=True,
        index=True,
    )
    username: str | None = Field(default=None, max_length=50, index=True)
    method: str = Field(max_length=10)
    path: str = Field(max_length=500, index=True)
    ip_address: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=500)
    status_code: int = Field(index=True)
    duration_ms: int
    operation_time: datetime = Field(default_factory=now_utc8_naive, index=True)


class ExceptionLogDo(SQLModel, table=True):
    """An unhandled API exception."""

    __tablename__ = "exception_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(
        default=None,
        foreign_key="users.id",
        ondelete="SET NULL",
        nullable=True,
        index=True,
    )
    username: str | None = Field(default=None, max_length=50)
    method: str = Field(max_length=10)
    path: str = Field(max_length=500, index=True)
    ip_address: str | None = Field(default=None, max_length=64)
    exception_type: str = Field(max_length=200, index=True)
    exception_message: str = Field(max_length=2000)
    traceback: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    exception_time: datetime = Field(default_factory=now_utc8_naive, index=True)
