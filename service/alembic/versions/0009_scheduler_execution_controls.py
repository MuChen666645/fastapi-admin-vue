"""增加任务超时、重试和执行控制字段。"""

import sqlalchemy as sa

from alembic import context, op

revision = "0009_scheduler_execution_controls"
down_revision = "0008_notice_recipients"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """幂等增加任务执行控制字段，兼容上次 DDL 已成功但版本号未更新的情况。"""
    if context.is_offline_mode():
        _add_columns()
        return
    bind = op.get_bind()
    columns = {
        column["name"] for column in sa.inspect(bind).get_columns("scheduled_jobs")
    }
    _add_columns(columns)


def downgrade() -> None:
    """删除任务执行控制字段。"""
    if context.is_offline_mode():
        op.drop_column("scheduled_jobs", "max_retries")
        op.drop_column("scheduled_jobs", "timeout_seconds")
        return
    bind = op.get_bind()
    columns = {
        column["name"] for column in sa.inspect(bind).get_columns("scheduled_jobs")
    }
    if "max_retries" in columns:
        op.drop_column("scheduled_jobs", "max_retries")
    if "timeout_seconds" in columns:
        op.drop_column("scheduled_jobs", "timeout_seconds")


def _add_columns(columns: set[str] | None = None) -> None:
    """在线模式按现有列幂等执行，离线模式生成完整迁移 SQL。"""
    if columns is None or "timeout_seconds" not in columns:
        op.add_column(
            "scheduled_jobs",
            sa.Column(
                "timeout_seconds",
                sa.Integer(),
                nullable=False,
                server_default="300",
            ),
        )
    if columns is None or "max_retries" not in columns:
        op.add_column(
            "scheduled_jobs",
            sa.Column(
                "max_retries",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
