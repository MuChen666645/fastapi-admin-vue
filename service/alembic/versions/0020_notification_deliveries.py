"""增加通知渠道投递和失败重试记录。"""

import sqlalchemy as sa

from alembic import op

revision = "0020_notification_deliveries"
down_revision = "0019_idempotency_batch_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建通知渠道投递表。"""
    op.create_table(
        "notification_deliveries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer()),
        sa.Column("notice_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("destination", sa.String(length=500)),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "next_attempt_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_error", sa.String(length=1000)),
        sa.Column("delivered_at", sa.DateTime()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["notice_id"], ["notices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "tenant_id",
        "notice_id",
        "user_id",
        "channel",
        "status",
        "next_attempt_at",
        "created_at",
    ):
        op.create_index(
            f"ix_notification_deliveries_{column}", "notification_deliveries", [column]
        )


def downgrade() -> None:
    """删除通知渠道投递表。"""
    for column in (
        "created_at",
        "next_attempt_at",
        "status",
        "channel",
        "user_id",
        "notice_id",
        "tenant_id",
    ):
        op.drop_index(
            f"ix_notification_deliveries_{column}", table_name="notification_deliveries"
        )
    op.drop_table("notification_deliveries")
