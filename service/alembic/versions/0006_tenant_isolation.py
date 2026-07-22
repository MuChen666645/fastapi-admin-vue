"""增加租户边界并为历史数据建立默认租户。"""

import sqlalchemy as sa

from alembic import op

revision = "0006_tenant_isolation"
down_revision = "0005_auth_security"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建租户表并将既有用户、角色归入默认租户。"""
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_tenants_code", "tenants", ["code"])
    op.create_index("ix_tenants_status", "tenants", ["status"])
    op.add_column("users", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.add_column("roles", sa.Column("tenant_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])
    op.create_foreign_key(
        "fk_users_tenant",
        "users",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_roles_tenant",
        "roles",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.execute(
        sa.text(
            "INSERT IGNORE INTO tenants "
            "(id, code, name, status, create_time, update_time) "
            "VALUES (1, 'default', '默认租户', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        )
    )
    op.execute(sa.text("UPDATE users SET tenant_id = 1 WHERE tenant_id IS NULL"))
    op.execute(sa.text("UPDATE roles SET tenant_id = 1 WHERE tenant_id IS NULL"))


def downgrade() -> None:
    """删除租户边界。"""
    op.drop_constraint("fk_roles_tenant", "roles", type_="foreignkey")
    op.drop_constraint("fk_users_tenant", "users", type_="foreignkey")
    op.drop_index("ix_roles_tenant_id", table_name="roles")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_column("roles", "tenant_id")
    op.drop_column("users", "tenant_id")
    op.drop_index("ix_tenants_status", table_name="tenants")
    op.drop_index("ix_tenants_code", table_name="tenants")
    op.drop_table("tenants")
