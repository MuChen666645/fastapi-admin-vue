"""增加用户敏感字段权限目录。"""

import sqlalchemy as sa

from alembic import op

revision = "0011_field_permissions"
down_revision = "0010_permission_change_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """插入字段级权限编码，具体授权仍由角色绑定控制。"""
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO permissions
                (name, code, module, permission_type, api_path, api_method,
                 status, create_time, update_time, remark)
            VALUES
                ('User Email Field', 'field:user:email', 'user', 'field', NULL, NULL,
                 '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'View user email field'),
                ('User Phone Field', 'field:user:phone', 'user', 'field', NULL, NULL,
                 '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'View user phone field'),
                ('User Avatar Field', 'field:user:avatar', 'user', 'field', NULL, NULL,
                 '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'View user avatar field')
            """
        )
    )


def downgrade() -> None:
    """删除字段级权限编码。"""
    op.execute(
        sa.text(
            "DELETE FROM permissions WHERE code IN "
            "('field:user:email', 'field:user:phone', 'field:user:avatar')"
        )
    )
