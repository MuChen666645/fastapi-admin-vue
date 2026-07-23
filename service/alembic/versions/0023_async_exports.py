"""创建持久化异步导出任务。"""

import sqlalchemy as sa

from alembic import op

revision = "0023_async_exports"
down_revision = "0022_role_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建异步导出任务表。"""
    op.create_table(
        "export_tasks",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("resource", sa.String(length=30), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("file_id", sa.String(length=36)),
        sa.Column("error_message", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["file_id"], ["file_metadata.file_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in (
        "tenant_id",
        "created_by",
        "resource",
        "status",
        "file_id",
        "created_at",
        "expires_at",
    ):
        op.create_index(f"ix_export_tasks_{column}", "export_tasks", [column])


def downgrade() -> None:
    """删除异步导出任务表。"""
    for column in (
        "expires_at",
        "created_at",
        "file_id",
        "status",
        "resource",
        "created_by",
        "tenant_id",
    ):
        op.drop_index(f"ix_export_tasks_{column}", table_name="export_tasks")
    op.drop_table("export_tasks")
