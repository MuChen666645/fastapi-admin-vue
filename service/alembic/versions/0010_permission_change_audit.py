"""增加权限变更版本审计。"""

import sqlalchemy as sa
from alembic import op


revision = "0010_permission_change_audit"
down_revision = "0009_scheduler_execution_controls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建不可变权限变更版本表。"""
    op.create_table(
        "permission_change_versions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("resource_type", sa.String(length=50), nullable=False),
        sa.Column("resource_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("before_json", sa.Text(), nullable=True),
        sa.Column("after_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_permission_change_versions_tenant_id",
        "permission_change_versions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_permission_change_versions_actor_user_id",
        "permission_change_versions",
        ["actor_user_id"],
    )
    op.create_index(
        "ix_permission_change_versions_resource_type",
        "permission_change_versions",
        ["resource_type"],
    )
    op.create_index(
        "ix_permission_change_versions_created_at",
        "permission_change_versions",
        ["created_at"],
    )


def downgrade() -> None:
    """删除权限变更版本审计。"""
    op.drop_index(
        "ix_permission_change_versions_created_at",
        table_name="permission_change_versions",
    )
    op.drop_index(
        "ix_permission_change_versions_resource_type",
        table_name="permission_change_versions",
    )
    op.drop_index(
        "ix_permission_change_versions_actor_user_id",
        table_name="permission_change_versions",
    )
    op.drop_index(
        "ix_permission_change_versions_tenant_id",
        table_name="permission_change_versions",
    )
    op.drop_table("permission_change_versions")
