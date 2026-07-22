"""为数据库备份接口补充权限目录。"""

import sqlalchemy as sa

from alembic import op

revision = "0017_backup_permissions"
down_revision = "0016_permission_version_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO permissions
                (name, code, module, permission_type, api_path, api_method,
                 status, create_time, update_time, remark)
            VALUES
                ('Backup create', 'system:backup:create', 'system', 'button',
                 '/ops/backup/create', 'POST', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, 'Database backup'),
                ('Backup restore', 'system:backup:restore', 'system', 'button',
                 '/ops/backup/restore', 'POST', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, 'Database restore')
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM permissions WHERE code IN "
            "('system:backup:create', 'system:backup:restore')"
        )
    )
