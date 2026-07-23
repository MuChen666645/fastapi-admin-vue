"""新增角色软删除和乐观锁字段。"""

import sqlalchemy as sa

from alembic import op

revision = "0022_role_lifecycle"
down_revision = "0021_tenant_operations_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """为角色增加生命周期字段，并保留已有数据。"""
    op.add_column(
        "roles", sa.Column("version", sa.Integer(), nullable=False, server_default="1")
    )
    op.add_column("roles", sa.Column("deleted_at", sa.DateTime()))
    op.create_index("ix_roles_deleted_at", "roles", ["deleted_at"])


def downgrade() -> None:
    """删除角色生命周期字段。"""
    op.drop_index("ix_roles_deleted_at", table_name="roles")
    op.drop_column("roles", "deleted_at")
    op.drop_column("roles", "version")
