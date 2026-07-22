"""创建角色与字段权限目录的关联表。"""

import sqlalchemy as sa
from alembic import op


revision = "0013_role_permissions"
down_revision = "0012_external_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "role_permission",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )


def downgrade() -> None:
    op.drop_table("role_permission")
