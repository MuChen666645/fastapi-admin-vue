"""增加任务超时、重试和执行控制字段。"""

import sqlalchemy as sa
from alembic import op


revision = "0009_scheduler_execution_controls"
down_revision = "0008_notice_recipients"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """幂等增加任务执行控制字段，兼容上次 DDL 已成功但版本号未更新的情况。"""
    bind = op.get_bind()
    columns = {
        column["name"]
        for column in sa.inspect(bind).get_columns("scheduled_jobs")
    }
    if "timeout_seconds" not in columns:
        op.add_column(
            "scheduled_jobs",
            sa.Column(
                "timeout_seconds",
                sa.Integer(),
                nullable=False,
                server_default="300",
            ),
        )
    if "max_retries" not in columns:
        op.add_column(
            "scheduled_jobs",
            sa.Column(
                "max_retries",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )


def downgrade() -> None:
    """删除任务执行控制字段。"""
    bind = op.get_bind()
    columns = {
        column["name"]
        for column in sa.inspect(bind).get_columns("scheduled_jobs")
    }
    if "max_retries" in columns:
        op.drop_column("scheduled_jobs", "max_retries")
    if "timeout_seconds" in columns:
        op.drop_column("scheduled_jobs", "timeout_seconds")
