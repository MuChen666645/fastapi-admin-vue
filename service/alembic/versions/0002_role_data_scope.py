"""增加角色数据权限配置。

Revision ID: 0002_role_data_scope
Revises: 0001_initial_schema
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_role_data_scope"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """增加角色数据权限模式和自定义部门关联。"""
    op.add_column(
        "roles",
        sa.Column(
            "data_scope",
            sa.String(length=1),
            nullable=False,
            server_default=sa.text("'5'"),
        ),
    )
    op.create_table(
        "role_dept",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("dept_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dept_id"], ["departments.dept_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "dept_id"),
    )
    op.create_index("ix_role_dept_dept_id", "role_dept", ["dept_id"])


def downgrade() -> None:
    """删除角色数据权限配置及其关联表。"""
    op.drop_index("ix_role_dept_dept_id", table_name="role_dept")
    op.drop_table("role_dept")
    op.drop_column("roles", "data_scope")
