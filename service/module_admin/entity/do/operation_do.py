"""幂等请求和批量操作审计模型。"""

from datetime import datetime

from sqlalchemy import Column, Text, UniqueConstraint
from sqlmodel import Field, SQLModel

from utils.time_utils import now_utc8_naive


class IdempotencyKeyDo(SQLModel, table=True):
    """一次写请求的幂等占位和响应缓存。"""

    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint(
            "scope_hash",
            "idempotency_key",
            "method",
            "path",
            name="uq_idempotency_scope_request",
        ),
    )

    id: str = Field(primary_key=True, max_length=36)
    tenant_id: int | None = Field(default=1, index=True)
    user_id: int | None = Field(default=None, index=True)
    scope_hash: str = Field(max_length=64, index=True)
    idempotency_key: str = Field(max_length=128, index=True)
    request_hash: str = Field(max_length=64)
    method: str = Field(max_length=10)
    path: str = Field(max_length=500)
    status_code: int = Field(default=0)
    response_body: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    response_content_type: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
    expires_at: datetime = Field(index=True)


class BatchOperationAuditDo(SQLModel, table=True):
    """批量业务操作的不可变审计记录。"""

    __tablename__ = "batch_operation_audits"

    id: str = Field(primary_key=True, max_length=36)
    tenant_id: int | None = Field(default=1, index=True)
    actor_user_id: int | None = Field(default=None, index=True)
    request_id: str | None = Field(default=None, max_length=128, index=True)
    operation: str = Field(max_length=50, index=True)
    resource_type: str = Field(max_length=50, index=True)
    resource_ids_json: str = Field(sa_column=Column(Text, nullable=False))
    before_json: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    after_json: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    status: str = Field(max_length=20, index=True)
    created_at: datetime = Field(default_factory=now_utc8_naive, index=True)
