"""增加外部身份提供商映射字段。"""

import sqlalchemy as sa
from alembic import op


revision = "0012_external_identity"
down_revision = "0011_field_permissions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """为用户保存外部身份提供商主体映射。"""
    op.add_column(
        "users",
        sa.Column("auth_provider", sa.String(length=20), nullable=False, server_default="local"),
    )
    op.add_column("users", sa.Column("auth_subject", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_users_auth_subject", "users", ["auth_subject"])
    op.create_index("ix_users_auth_provider", "users", ["auth_provider"])


def downgrade() -> None:
    """删除外部身份提供商主体映射。"""
    op.drop_index("ix_users_auth_provider", table_name="users")
    op.drop_constraint("uq_users_auth_subject", "users", type_="unique")
    op.drop_column("users", "auth_subject")
    op.drop_column("users", "auth_provider")
