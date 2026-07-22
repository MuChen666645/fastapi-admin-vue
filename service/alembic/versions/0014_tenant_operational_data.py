"""为运营数据表补充租户边界。"""

import sqlalchemy as sa

from alembic import op

revision = "0014_tenant_operational_data"
down_revision = "0013_role_permissions"
branch_labels = None
depends_on = None

TABLES = (
    "dict_types",
    "dict_data",
    "menu",
    "departments",
    "posts",
    "system_configs",
    "notices",
    "file_metadata",
    "scheduled_jobs",
    "job_logs",
    "login_logs",
    "operation_logs",
    "exception_logs",
)


def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(table_name, sa.Column("tenant_id", sa.Integer(), nullable=True))
        op.create_index(f"ix_{table_name}_tenant_id", table_name, ["tenant_id"])
        op.create_foreign_key(
            f"fk_{table_name}_tenant",
            table_name,
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.execute(
            sa.text(f"UPDATE {table_name} SET tenant_id = 1 WHERE tenant_id IS NULL")
        )


def downgrade() -> None:
    for table_name in reversed(TABLES):
        op.drop_constraint(f"fk_{table_name}_tenant", table_name, type_="foreignkey")
        op.drop_index(f"ix_{table_name}_tenant_id", table_name=table_name)
        op.drop_column(table_name, "tenant_id")
