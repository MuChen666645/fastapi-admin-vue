"""防止并发权限变更产生重复版本号。"""

from alembic import op

revision = "0016_permission_version_unique"
down_revision = "0015_file_chunk_uploads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_permission_change_resource_version",
        "permission_change_versions",
        ["resource_type", "resource_id", "version"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_permission_change_resource_version",
        "permission_change_versions",
        type_="unique",
    )
