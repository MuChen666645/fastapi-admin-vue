"""增加写请求幂等和批量操作审计表。"""

import sqlalchemy as sa

from alembic import op

revision = "0019_idempotency_batch_audit"
down_revision = "0018_tenant_memberships"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建幂等占位和批量审计表。"""
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer()),
        sa.Column("user_id", sa.Integer()),
        sa.Column("scope_hash", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("response_body", sa.Text()),
        sa.Column("response_content_type", sa.String(length=255)),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "scope_hash",
            "idempotency_key",
            "method",
            "path",
            name="uq_idempotency_scope_request",
        ),
    )
    op.create_index("ix_idempotency_keys_tenant_id", "idempotency_keys", ["tenant_id"])
    op.create_index("ix_idempotency_keys_user_id", "idempotency_keys", ["user_id"])
    op.create_index(
        "ix_idempotency_keys_scope_hash", "idempotency_keys", ["scope_hash"]
    )
    op.create_index(
        "ix_idempotency_keys_idempotency_key", "idempotency_keys", ["idempotency_key"]
    )
    op.create_index(
        "ix_idempotency_keys_created_at", "idempotency_keys", ["created_at"]
    )
    op.create_index(
        "ix_idempotency_keys_expires_at", "idempotency_keys", ["expires_at"]
    )
    op.create_table(
        "batch_operation_audits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer()),
        sa.Column("actor_user_id", sa.Integer()),
        sa.Column("request_id", sa.String(length=128)),
        sa.Column("operation", sa.String(length=50), nullable=False),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_ids_json", sa.Text(), nullable=False),
        sa.Column("before_json", sa.Text()),
        sa.Column("after_json", sa.Text()),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "tenant_id",
        "actor_user_id",
        "request_id",
        "operation",
        "resource_type",
        "status",
        "created_at",
    ):
        op.create_index(
            f"ix_batch_operation_audits_{column}", "batch_operation_audits", [column]
        )


def downgrade() -> None:
    """删除幂等和批量审计表。"""
    for column in (
        "created_at",
        "status",
        "resource_type",
        "operation",
        "request_id",
        "actor_user_id",
        "tenant_id",
    ):
        op.drop_index(
            f"ix_batch_operation_audits_{column}", table_name="batch_operation_audits"
        )
    op.drop_table("batch_operation_audits")
    for column in (
        "expires_at",
        "created_at",
        "idempotency_key",
        "scope_hash",
        "user_id",
        "tenant_id",
    ):
        op.drop_index(f"ix_idempotency_keys_{column}", table_name="idempotency_keys")
    op.drop_table("idempotency_keys")
