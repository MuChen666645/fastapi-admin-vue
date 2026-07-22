"""增加通知收件人和已读状态。"""

import sqlalchemy as sa
from alembic import op


revision = "0008_notice_recipients"
down_revision = "0007_api_permission_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建通知收件人关联表。"""
    op.create_table(
        "notice_recipients",
        sa.Column("notice_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["notice_id"], ["notices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("notice_id", "user_id"),
    )
    op.create_index("ix_notice_recipients_user_id", "notice_recipients", ["user_id"])
    op.create_index("ix_notice_recipients_read_at", "notice_recipients", ["read_at"])


def downgrade() -> None:
    """删除通知收件人关联表。"""
    op.drop_index("ix_notice_recipients_read_at", table_name="notice_recipients")
    op.drop_index("ix_notice_recipients_user_id", table_name="notice_recipients")
    op.drop_table("notice_recipients")
