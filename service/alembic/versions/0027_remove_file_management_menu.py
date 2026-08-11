"""清理已移除的文件管理菜单。"""

import sqlalchemy as sa

from alembic import op

revision = "0027_remove_file_management_menu"
down_revision = "0026_message_center"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE rm
            FROM role_menu AS rm
            INNER JOIN menu AS m ON m.menu_id = rm.menu_id
            WHERE m.menu_id IN (350, 370, 371, 372)
            """
        )
    )
    op.execute(
        sa.text(
            """
            DELETE FROM menu
            WHERE menu_id IN (370, 371, 372)
            """
        )
    )
    op.execute(sa.text("DELETE FROM menu WHERE menu_id = 350"))


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO menu (
                tenant_id, menu_id, parent_id, menu_name, icon, menu_path,
                component, is_hidden, is_cache, menu_type, sort, link_url,
                perms, status, create_time, update_time, remark
            ) VALUES
                (1, 350, 2, '文件管理', 'FolderOpenOutline', 'file',
                 'system/file/index', '0', '1', 'C', 7, NULL,
                 'system:file:upload', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, '文件管理'),
                (1, 370, 350, '文件上传', NULL, NULL, NULL, '0', '0', 'F', 1,
                 NULL, 'system:file:upload', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, '文件上传权限'),
                (1, 371, 350, '文件下载', NULL, NULL, NULL, '0', '0', 'F', 2,
                 NULL, 'system:file:download', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, '文件下载权限'),
                (1, 372, 350, '文件删除', NULL, NULL, NULL, '0', '0', 'F', 3,
                 NULL, 'system:file:remove', '1', CURRENT_TIMESTAMP,
                 CURRENT_TIMESTAMP, '文件删除权限')
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO role_menu (role_id, menu_id)
            SELECT r.id, m.menu_id
            FROM roles AS r
            INNER JOIN menu AS m ON m.tenant_id = r.tenant_id
            WHERE r.code = 'admin'
              AND r.tenant_id = 1
              AND m.menu_id IN (350, 370, 371, 372)
            """
        )
    )
