"""为角色编码增加唯一索引。"""

from alembic import op


revision = "0004_role_code_unique"
down_revision = "0003_admin_operations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """确保角色编码在数据库层面唯一。"""
    op.create_index("uq_roles_code", "roles", ["code"], unique=True)


def downgrade() -> None:
    """删除角色编码唯一索引。"""
    op.drop_index("uq_roles_code", table_name="roles")
