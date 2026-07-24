"""为关联授权和通知投递补齐租户与租约字段。"""

import sqlalchemy as sa

from alembic import context, op

revision = "0025_security_consistency"
down_revision = "0024_password_reset_tenant_permissions"
branch_labels = None
depends_on = None


def _is_offline_mode() -> bool:
    try:
        return context.is_offline_mode()
    except NameError:
        return False


def _assert_no_cross_tenant_duplicates(table: str, value_column: str) -> None:
    if _is_offline_mode():
        return
    duplicate = op.get_bind().execute(
        sa.text(
            f"SELECT user_id, {value_column} "
            f"FROM {table} "
            f"GROUP BY user_id, {value_column} "
            "HAVING COUNT(*) > 1 LIMIT 1"
        )
    ).first()
    if duplicate is not None:
        raise RuntimeError(
            f"无法安全降级 {revision}：{table} 存在跨租户重复关联，拒绝丢失授权数据"
        )


def _column_exists(table: str, column: str) -> bool:
    if _is_offline_mode():
        return False
    return bool(
        op.get_bind()
        .execute(
            sa.text(
                "SELECT COUNT(*) "
                "FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() "
                "AND TABLE_NAME = :table_name "
                "AND COLUMN_NAME = :column_name"
            ),
            {"table_name": table, "column_name": column},
        )
        .scalar()
    )


RELATION_FOREIGN_KEYS = {
    "user_role": (
        ("fk_user_role_user", "users", "user_id", "id", "CASCADE"),
        ("fk_user_role_role", "roles", "role_id", "id", "CASCADE"),
    ),
    "user_post": (
        ("fk_user_post_user", "users", "user_id", "id", "CASCADE"),
        ("fk_user_post_post", "posts", "post_id", "post_id", "RESTRICT"),
    ),
}


def _drop_relation_foreign_keys(table: str, *, legacy_names: bool = False) -> None:
    """主键切换前移除依赖旧主键的外键，兼容历史约束名称。"""
    if _is_offline_mode():
        if legacy_names:
            names = [
                f"{table}_ibfk_{index}"
                for index in range(1, len(RELATION_FOREIGN_KEYS[table]) + 1)
            ]
        else:
            names = [item[0] for item in RELATION_FOREIGN_KEYS[table]]
    else:
        names = list(
            op.get_bind()
            .execute(
                sa.text(
                    "SELECT CONSTRAINT_NAME "
                    "FROM information_schema.KEY_COLUMN_USAGE "
                    "WHERE CONSTRAINT_SCHEMA = DATABASE() "
                    "AND TABLE_NAME = :table_name "
                    "AND REFERENCED_TABLE_NAME IS NOT NULL "
                    "AND COLUMN_NAME <> 'tenant_id'"
                ),
                {"table_name": table},
            )
            .scalars()
        )
    for name in names:
        op.drop_constraint(name, table_name=table, type_="foreignkey")


def _create_relation_foreign_keys(table: str) -> None:
    for (
        name,
        referred_table,
        local_column,
        referred_column,
        ondelete,
    ) in RELATION_FOREIGN_KEYS[table]:
        op.create_foreign_key(
            name,
            table,
            referred_table,
            [local_column],
            [referred_column],
            ondelete=ondelete,
        )


def upgrade() -> None:
    """让用户角色、岗位关联按租户隔离，并增加通知投递租约。"""
    for table, source_table, source_id, relation_id in (
        ("user_role", "roles", "id", "role_id"),
        ("user_post", "posts", "post_id", "post_id"),
    ):
        if not _column_exists(table, "tenant_id"):
            op.add_column(table, sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.execute(
            sa.text(
                f"UPDATE {table} AS relation "
                f"JOIN {source_table} AS source ON source.{source_id} = relation.{relation_id} "
                "SET relation.tenant_id = COALESCE(source.tenant_id, 1)"
            )
        )
        op.alter_column(
            table,
            "tenant_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        _drop_relation_foreign_keys(table, legacy_names=True)
        op.drop_constraint("PRIMARY", table_name=table, type_="primary")
        if table == "user_role":
            primary_columns = ["tenant_id", "user_id", "role_id"]
        else:
            primary_columns = ["tenant_id", "user_id", "post_id"]
        op.create_primary_key(
            f"pk_{table}", table, primary_columns
        )
        op.create_foreign_key(
            f"fk_{table}_tenant",
            table,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])
        _create_relation_foreign_keys(table)

    op.add_column(
        "notification_deliveries",
        sa.Column("lease_token", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "notification_deliveries",
        sa.Column("lease_until", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_notification_deliveries_lease_until",
        "notification_deliveries",
        ["lease_until"],
    )


def downgrade() -> None:
    """仅在不会折叠跨租户关联时恢复旧结构。"""
    _assert_no_cross_tenant_duplicates("user_role", "role_id")
    _assert_no_cross_tenant_duplicates("user_post", "post_id")
    op.drop_index(
        "ix_notification_deliveries_lease_until",
        table_name="notification_deliveries",
    )
    op.drop_column("notification_deliveries", "lease_until")
    op.drop_column("notification_deliveries", "lease_token")
    for table in ("user_post", "user_role"):
        _drop_relation_foreign_keys(table)
        op.drop_index(f"ix_{table}_tenant_id", table_name=table)
        op.drop_constraint(f"fk_{table}_tenant", table_name=table, type_="foreignkey")
        op.drop_constraint(f"pk_{table}", table_name=table, type_="primary")
        op.create_primary_key(
            f"pk_{table}_legacy",
            table,
            ["user_id", "post_id"] if table == "user_post" else ["user_id", "role_id"],
        )
        op.drop_column(table, "tenant_id")
        _create_relation_foreign_keys(table)
