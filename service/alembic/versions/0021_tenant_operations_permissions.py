"""新增租户、密钥轮换和备份验证权限。"""

import sqlalchemy as sa

from alembic import op

revision = "0021_tenant_operations_permissions"
down_revision = "0020_notification_deliveries"
branch_labels = None
depends_on = None


PERMISSIONS = (
    ("Tenant list", "system:tenant:list", "GET", "/tenant/list/all"),
    ("Tenant add", "system:tenant:add", "POST", "/tenant/add"),
    ("Tenant edit", "system:tenant:edit", "PUT", "/tenant/{tenant_id}"),
    ("Tenant remove", "system:tenant:remove", "DELETE", "/tenant/{tenant_id}"),
    (
        "Tenant member list",
        "system:tenant:member:list",
        "GET",
        "/tenant/{tenant_id}/members",
    ),
    (
        "Tenant member add",
        "system:tenant:member:add",
        "POST",
        "/tenant/{tenant_id}/members",
    ),
    (
        "Tenant member edit",
        "system:tenant:member:edit",
        "PUT",
        "/tenant/{tenant_id}/members/{user_id}",
    ),
    (
        "Tenant member remove",
        "system:tenant:member:remove",
        "DELETE",
        "/tenant/{tenant_id}/members/{user_id}",
    ),
    ("Secret rotation", "system:secret:rotate", "POST", "/ops/secrets/rotate"),
    (
        "Backup verification",
        "system:backup:verify",
        "POST",
        "/ops/backup/verify",
    ),
    (
        "Backup restore rehearsal",
        "system:backup:rehearse",
        "POST",
        "/ops/backup/rehearse",
    ),
)


def upgrade() -> None:
    """写入租户和运维接口使用的权限。"""
    values = ",\n".join(
        "('{}', '{}', 'system', 'button', '{}', '{}', '1', CURRENT_TIMESTAMP, "
        "CURRENT_TIMESTAMP, '{}')".format(
            name,
            code,
            path,
            method,
            name,
        )
        for name, code, method, path in PERMISSIONS
    )
    # 兼容已经通过初始化 SQL 写入权限的数据库，保证迁移可以重复执行。
    op.execute(
        sa.text(
            "INSERT IGNORE INTO permissions "
            "(name, code, module, permission_type, api_path, api_method, status, "
            "create_time, update_time, remark) VALUES " + values
        )
    )


def downgrade() -> None:
    """仅删除本次迁移新增的权限。"""
    codes = ", ".join(f"'{code}'" for _, code, _, _ in PERMISSIONS)
    op.execute(sa.text(f"DELETE FROM permissions WHERE code IN ({codes})"))
