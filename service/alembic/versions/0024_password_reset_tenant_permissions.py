"""绑定密码找回令牌租户并允许同一路由登记多个权限。"""

import sqlalchemy as sa

from alembic import op

revision = "0024_password_reset_tenant_permissions"
down_revision = "0023_async_exports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """补齐租户边界，并把权限目录唯一键扩展到权限编码。"""
    op.add_column(
        "password_reset_tokens",
        sa.Column("tenant_id", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            "UPDATE password_reset_tokens AS reset_token "
            "JOIN users AS user ON user.id = reset_token.user_id "
            "SET reset_token.tenant_id = COALESCE(user.tenant_id, 1)"
        )
    )
    op.alter_column(
        "password_reset_tokens",
        "tenant_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_password_reset_tokens_tenant_id",
        "password_reset_tokens",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_password_reset_tokens_tenant_id",
        "password_reset_tokens",
        ["tenant_id"],
    )

    # 0007 创建的是未命名 MySQL 唯一约束，MySQL 会使用首列名作为索引名。
    op.drop_index("api_path", table_name="api_permission_catalog")
    op.create_unique_constraint(
        "uq_api_permission_catalog_path_method_code",
        "api_permission_catalog",
        ["api_path", "api_method", "permission_code"],
    )


def downgrade() -> None:
    """恢复旧权限目录约束并删除令牌租户字段。"""
    duplicate = op.get_bind().execute(
        sa.text(
            "SELECT api_path, api_method "
            "FROM api_permission_catalog "
            "GROUP BY api_path, api_method "
            "HAVING COUNT(*) > 1 "
            "LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            "无法安全降级 0024：权限目录存在同一路由的多个权限，请先人工处理冲突"
        )
    op.drop_constraint(
        "uq_api_permission_catalog_path_method_code",
        "api_permission_catalog",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_api_permission_catalog_path_method",
        "api_permission_catalog",
        ["api_path", "api_method"],
    )
    op.drop_index(
        "ix_password_reset_tokens_tenant_id",
        table_name="password_reset_tokens",
    )
    op.drop_constraint(
        "fk_password_reset_tokens_tenant_id",
        "password_reset_tokens",
        type_="foreignkey",
    )
    op.drop_column("password_reset_tokens", "tenant_id")
