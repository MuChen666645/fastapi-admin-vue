"""补齐租户管理和系统参数菜单。"""

import sqlalchemy as sa

from alembic import op

revision = "0028_tenant_and_system_parameter_menus"
down_revision = "0027_remove_file_management_menu"
branch_labels = None
depends_on = None

TENANT_MENU_ID = 353
TENANT_BUTTON_MENUS = (
    (389, "租户列表", "system:tenant:list", "租户列表权限"),
    (390, "租户新增", "system:tenant:add", "租户新增权限"),
    (391, "租户编辑", "system:tenant:edit", "租户编辑权限"),
    (392, "租户删除", "system:tenant:remove", "租户删除权限"),
    (393, "租户成员列表", "system:tenant:member:list", "租户成员列表权限"),
    (394, "租户成员新增", "system:tenant:member:add", "租户成员新增权限"),
    (395, "租户成员编辑", "system:tenant:member:edit", "租户成员编辑权限"),
    (396, "租户成员删除", "system:tenant:member:remove", "租户成员删除权限"),
)
TENANT_MENU_IDS = (TENANT_MENU_ID,) + tuple(item[0] for item in TENANT_BUTTON_MENUS)


def upgrade() -> None:
    """为默认租户补齐平台租户管理和系统参数菜单。"""
    op.execute(
        sa.text(
            "INSERT IGNORE INTO menu ("
            "tenant_id, menu_id, parent_id, menu_name, icon, menu_path, "
            "component, is_hidden, is_cache, menu_type, sort, link_url, perms, "
            "status, create_time, update_time, remark) VALUES "
            "(1, :menu_id, 2, '租户管理', 'BusinessOutline', 'tenant', "
            "'system/tenant/index', '0', '1', 'C', 10, NULL, "
            "'system:tenant:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "
            "'租户管理菜单')"
        ).bindparams(menu_id=TENANT_MENU_ID)
    )
    op.execute(
        sa.text(
            "UPDATE menu SET menu_name = '系统参数', menu_path = 'config', "
            "component = 'system/config/index', icon = 'SettingsOutline', "
            "perms = 'system:config:list', remark = '系统参数管理菜单' "
            "WHERE tenant_id = 1 AND menu_id = 351"
        )
    )
    op.execute(
        sa.text(
            "UPDATE menu SET parent_id = 2, menu_name = '租户管理', "
            "icon = 'BusinessOutline', menu_path = 'tenant', "
            "component = 'system/tenant/index', is_hidden = '0', is_cache = '1', "
            "menu_type = 'C', sort = 10, link_url = NULL, "
            "perms = 'system:tenant:list', status = '1', "
            "remark = '租户管理菜单', update_time = CURRENT_TIMESTAMP "
            "WHERE tenant_id = 1 AND menu_id = :menu_id"
        ).bindparams(menu_id=TENANT_MENU_ID)
    )

    for menu_id, menu_name, permission, remark in TENANT_BUTTON_MENUS:
        op.execute(
            sa.text(
                "INSERT IGNORE INTO menu ("
                "tenant_id, menu_id, parent_id, menu_name, icon, menu_path, "
                "component, is_hidden, is_cache, menu_type, sort, link_url, perms, "
                "status, create_time, update_time, remark) VALUES "
                "(1, :menu_id, :parent_id, :menu_name, NULL, NULL, NULL, "
                "'0', '0', 'F', :sort, NULL, :permission, '1', "
                "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :remark)"
            ).bindparams(
                menu_id=menu_id,
                parent_id=TENANT_MENU_ID,
                menu_name=menu_name,
                sort=menu_id - TENANT_BUTTON_MENUS[0][0] + 1,
                permission=permission,
                remark=remark,
            )
        )
        op.execute(
            sa.text(
                "UPDATE menu SET parent_id = :parent_id, menu_name = :menu_name, "
                "perms = :permission, menu_type = 'F', sort = :sort, "
                "remark = :remark, update_time = CURRENT_TIMESTAMP "
                "WHERE tenant_id = 1 AND menu_id = :menu_id"
            ).bindparams(
                menu_id=menu_id,
                parent_id=TENANT_MENU_ID,
                menu_name=menu_name,
                sort=menu_id - TENANT_BUTTON_MENUS[0][0] + 1,
                permission=permission,
                remark=remark,
            )
        )

    op.execute(
        sa.text(
            "INSERT IGNORE INTO role_menu (role_id, menu_id) "
            "SELECT r.id, m.menu_id FROM roles AS r "
            "INNER JOIN menu AS m ON m.tenant_id = r.tenant_id "
            "WHERE r.code = 'admin' AND r.tenant_id = 1 "
            "AND m.menu_id IN :menu_ids"
        ).bindparams(sa.bindparam("menu_ids", expanding=True, value=TENANT_MENU_IDS))
    )


def downgrade() -> None:
    """移除本迁移补齐的默认租户菜单及其管理员授权。"""
    op.execute(
        sa.text(
            "DELETE rm FROM role_menu AS rm "
            "INNER JOIN menu AS m ON m.menu_id = rm.menu_id "
            "WHERE m.tenant_id = 1 "
            "AND m.menu_id IN :menu_ids"
        ).bindparams(sa.bindparam("menu_ids", expanding=True, value=TENANT_MENU_IDS))
    )
    op.execute(
        sa.text(
            "DELETE FROM menu WHERE tenant_id = 1 " "AND menu_id IN :menu_ids"
        ).bindparams(sa.bindparam("menu_ids", expanding=True, value=TENANT_MENU_IDS))
    )
    op.execute(
        sa.text(
            "UPDATE menu SET menu_name = '系统配置', remark = '系统配置' "
            "WHERE tenant_id = 1 AND menu_id = 351"
        )
    )
