"""增加租户成员关系、软删除和乐观锁字段。"""

import sqlalchemy as sa

from alembic import op

revision = "0018_tenant_memberships"
down_revision = "0017_backup_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建租户成员关系并为租户启用安全生命周期字段。"""
    op.add_column(
        "users", sa.Column("version", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("users", sa.Column("deleted_at", sa.DateTime()))
    op.create_index("ix_users_deleted_at", "users", ["deleted_at"])
    op.add_column("tenants", sa.Column("description", sa.String(length=500)))
    op.add_column(
        "tenants",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("tenants", sa.Column("deleted_at", sa.DateTime()))
    op.create_index("ix_tenants_deleted_at", "tenants", ["deleted_at"])
    op.create_table(
        "tenant_members",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False, server_default="1"),
        sa.Column(
            "is_default", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("deleted_at", sa.DateTime()),
        sa.Column(
            "joined_at",
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "tenant_id"),
    )
    op.create_index("ix_tenant_members_tenant_id", "tenant_members", ["tenant_id"])
    op.create_index("ix_tenant_members_status", "tenant_members", ["status"])
    op.create_index("ix_tenant_members_deleted_at", "tenant_members", ["deleted_at"])
    op.execute(
        sa.text(
            "INSERT IGNORE INTO tenant_members "
            "(user_id, tenant_id, status, is_default, version, joined_at, updated_at) "
            "SELECT id, tenant_id, status, TRUE, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP "
            "FROM users WHERE tenant_id IS NOT NULL"
        )
    )


def downgrade() -> None:
    """删除租户成员关系和生命周期字段。"""
    op.drop_index("ix_tenant_members_deleted_at", table_name="tenant_members")
    op.drop_index("ix_tenant_members_status", table_name="tenant_members")
    op.drop_index("ix_tenant_members_tenant_id", table_name="tenant_members")
    op.drop_table("tenant_members")
    op.drop_index("ix_tenants_deleted_at", table_name="tenants")
    op.drop_column("tenants", "deleted_at")
    op.drop_column("tenants", "version")
    op.drop_column("tenants", "description")
    op.drop_index("ix_users_deleted_at", table_name="users")
    op.drop_column("users", "deleted_at")
    op.drop_column("users", "version")
