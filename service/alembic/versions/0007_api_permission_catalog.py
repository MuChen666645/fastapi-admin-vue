"""增加自动同步的 API 权限目录。"""

import sqlalchemy as sa
from alembic import op


revision = "0007_api_permission_catalog"
down_revision = "0006_tenant_isolation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建 API 路由权限目录。"""
    op.create_table(
        "api_permission_catalog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("permission_code", sa.String(length=100), nullable=False),
        sa.Column("api_path", sa.String(length=255), nullable=False),
        sa.Column("api_method", sa.String(length=20), nullable=False),
        sa.Column("route_name", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("api_path", "api_method"),
    )
    op.create_index(
        "ix_api_permission_catalog_permission_code",
        "api_permission_catalog",
        ["permission_code"],
    )
    op.create_index(
        "ix_api_permission_catalog_status",
        "api_permission_catalog",
        ["status"],
    )
    op.create_index(
        "ix_api_permission_catalog_last_seen_at",
        "api_permission_catalog",
        ["last_seen_at"],
    )


def downgrade() -> None:
    """删除 API 路由权限目录。"""
    op.drop_index(
        "ix_api_permission_catalog_last_seen_at",
        table_name="api_permission_catalog",
    )
    op.drop_index(
        "ix_api_permission_catalog_status",
        table_name="api_permission_catalog",
    )
    op.drop_index(
        "ix_api_permission_catalog_permission_code",
        table_name="api_permission_catalog",
    )
    op.drop_table("api_permission_catalog")
