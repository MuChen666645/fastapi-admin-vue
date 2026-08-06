"""将通知公告资源重构为消息中心。"""

import sqlalchemy as sa

from alembic import context, op

revision = "0026_message_center"
down_revision = "0025_security_consistency"
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _column_names(table_name: str) -> set[str]:
    return {
        column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)
    }


def _rename_table(old_name: str, new_name: str) -> None:
    if context.is_offline_mode():
        op.rename_table(old_name, new_name)
        return
    tables = _table_names()
    if old_name in tables and new_name in tables:
        raise RuntimeError(
            f"Cannot rename {old_name}: both {old_name} and {new_name} exist"
        )
    if old_name in tables:
        op.rename_table(old_name, new_name)
        return
    if new_name not in tables:
        raise RuntimeError(f"Neither {old_name} nor {new_name} exists")


def _rename_column(
    table_name: str,
    old_name: str,
    new_name: str,
    *,
    existing_type: sa.types.TypeEngine,
    existing_nullable: bool,
) -> None:
    if context.is_offline_mode():
        op.alter_column(
            table_name,
            old_name,
            new_column_name=new_name,
            existing_type=existing_type,
            existing_nullable=existing_nullable,
        )
        return
    columns = _column_names(table_name)
    if old_name in columns and new_name in columns:
        raise RuntimeError(f"Cannot rename {table_name}.{old_name}: both columns exist")
    if old_name in columns:
        op.alter_column(
            table_name,
            old_name,
            new_column_name=new_name,
            existing_type=existing_type,
            existing_nullable=existing_nullable,
        )
        return
    if new_name not in columns:
        raise RuntimeError(
            f"Neither {table_name}.{old_name} nor {table_name}.{new_name} exists"
        )


def _rename_index(table_name: str, old_name: str, new_name: str) -> None:
    if context.is_offline_mode():
        op.execute(
            sa.text(f"ALTER TABLE {table_name} RENAME INDEX {old_name} TO {new_name}")
        )
        return
    indexes = {
        index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)
    }
    if old_name in indexes and new_name in indexes:
        raise RuntimeError(f"Cannot rename {table_name}.{old_name}: both indexes exist")
    if old_name not in indexes and new_name not in indexes:
        raise RuntimeError(f"Neither index {old_name} nor {new_name} exists")
    if new_name in indexes:
        return
    op.execute(
        sa.text(f"ALTER TABLE {table_name} RENAME INDEX {old_name} TO {new_name}")
    )


def _rename_message_tables() -> None:
    _rename_table("notices", "messages")
    _rename_column(
        "messages",
        "notice_title",
        "message_title",
        existing_type=sa.String(length=100),
        existing_nullable=False,
    )
    _rename_column(
        "messages",
        "notice_type",
        "message_type",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )
    _rename_column(
        "messages",
        "notice_content",
        "message_content",
        existing_type=sa.Text(),
        existing_nullable=False,
    )

    _rename_table("notice_recipients", "message_recipients")
    _rename_column(
        "message_recipients",
        "notice_id",
        "message_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    _rename_table("notification_deliveries", "message_deliveries")
    _rename_column(
        "message_deliveries",
        "notice_id",
        "message_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    for old_name, new_name in (
        ("ix_notices_notice_title", "ix_messages_message_title"),
        ("ix_notices_notice_type", "ix_messages_message_type"),
        ("ix_notices_status", "ix_messages_status"),
        ("ix_notices_publish_time", "ix_messages_publish_time"),
        ("ix_notices_create_by", "ix_messages_create_by"),
        ("ix_notices_tenant_id", "ix_messages_tenant_id"),
    ):
        _rename_index("messages", old_name, new_name)
    for old_name, new_name in (
        ("ix_notice_recipients_user_id", "ix_message_recipients_user_id"),
        ("ix_notice_recipients_read_at", "ix_message_recipients_read_at"),
    ):
        _rename_index("message_recipients", old_name, new_name)
    for old_name, new_name in (
        (
            "ix_notification_deliveries_tenant_id",
            "ix_message_deliveries_tenant_id",
        ),
        ("ix_notification_deliveries_notice_id", "ix_message_deliveries_message_id"),
        ("ix_notification_deliveries_user_id", "ix_message_deliveries_user_id"),
        ("ix_notification_deliveries_channel", "ix_message_deliveries_channel"),
        ("ix_notification_deliveries_status", "ix_message_deliveries_status"),
        (
            "ix_notification_deliveries_next_attempt_at",
            "ix_message_deliveries_next_attempt_at",
        ),
        (
            "ix_notification_deliveries_created_at",
            "ix_message_deliveries_created_at",
        ),
        (
            "ix_notification_deliveries_lease_until",
            "ix_message_deliveries_lease_until",
        ),
    ):
        _rename_index("message_deliveries", old_name, new_name)


def _rename_permissions(
    source_prefix: str,
    target_prefix: str,
    names: tuple[str, ...],
    target_label: str,
) -> None:
    resource_name = target_prefix.rsplit(":", maxsplit=1)[-1]
    id_name = f"{resource_name}_id"
    for name in names:
        source_code = f"{source_prefix}:{name}"
        target_code = f"{target_prefix}:{name}"
        permission_name = (
            target_label
            + {
                "list": "列表",
                "query": "查询",
                "add": "新增",
                "edit": "编辑",
                "remove": "删除",
            }[name]
        )
        path = (
            f"/{resource_name}/list"
            if name == "list"
            else (
                f"/{resource_name}/add"
                if name == "add"
                else f"/{resource_name}/{{{id_name}}}"
            )
        )
        method = (
            "GET"
            if name in {"list", "query"}
            else "POST" if name == "add" else "PUT" if name == "edit" else "DELETE"
        )
        _merge_permission_definition(
            source_code,
            target_code,
            permission_name,
            path,
            method,
            f"{permission_name}权限",
        )
        _merge_permission_catalog(source_code, target_code, path, method)


def _merge_permission_definition(
    source_code: str,
    target_code: str,
    name: str,
    path: str,
    method: str,
    remark: str,
) -> None:
    op.execute(
        sa.text(
            "UPDATE menu SET perms = :target_code " "WHERE perms = :source_code"
        ).bindparams(target_code=target_code, source_code=source_code)
    )
    op.execute(
        sa.text(
            "DELETE source FROM permissions AS source "
            "INNER JOIN permissions AS target ON target.code = :target_code "
            "WHERE source.code = :source_code"
        ).bindparams(target_code=target_code, source_code=source_code)
    )
    op.execute(
        sa.text(
            "UPDATE permissions SET name = :name, code = :target_code, "
            "api_path = :api_path, api_method = :api_method, remark = :remark "
            "WHERE code = :source_code OR code = :target_code"
        ).bindparams(
            name=name,
            target_code=target_code,
            api_path=path,
            api_method=method,
            remark=remark,
            source_code=source_code,
        )
    )


def _merge_permission_catalog(
    source_code: str,
    target_code: str,
    path: str,
    method: str,
) -> None:
    op.execute(
        sa.text(
            "DELETE source FROM api_permission_catalog AS source "
            "INNER JOIN api_permission_catalog AS target "
            "ON target.permission_code = :target_code "
            "AND target.api_path = :api_path "
            "AND target.api_method = :api_method "
            "WHERE source.permission_code = :source_code"
        ).bindparams(
            target_code=target_code,
            api_path=path,
            api_method=method,
            source_code=source_code,
        )
    )
    op.execute(
        sa.text(
            "DELETE duplicate FROM api_permission_catalog AS duplicate "
            "INNER JOIN api_permission_catalog AS keeper "
            "ON keeper.permission_code = :source_code "
            "AND keeper.id < duplicate.id "
            "WHERE duplicate.permission_code = :source_code"
        ).bindparams(source_code=source_code)
    )
    op.execute(
        sa.text(
            "UPDATE api_permission_catalog SET permission_code = :target_code, "
            "api_path = :api_path, api_method = :api_method "
            "WHERE permission_code = :source_code"
        ).bindparams(
            target_code=target_code,
            api_path=path,
            api_method=method,
            source_code=source_code,
        )
    )


def _clear_legacy_message_seeds() -> None:
    op.execute(
        sa.text(
            "DELETE FROM message_deliveries "
            "WHERE tenant_id = 1 AND message_id BETWEEN 400 AND 414"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM message_recipients " "WHERE message_id BETWEEN 400 AND 414"
        )
    )
    op.execute(
        sa.text("DELETE FROM messages WHERE tenant_id = 1 AND id BETWEEN 400 AND 414")
    )


def upgrade() -> None:
    """将历史通知公告表和权限资源迁移为消息中心。"""
    _rename_message_tables()
    _rename_permissions(
        "system:notice",
        "system:message",
        ("list", "query", "add", "edit", "remove"),
        "消息",
    )
    op.execute(
        sa.text(
            "UPDATE menu SET menu_name = '消息中心', menu_path = 'message', "
            "component = 'system/message/index', perms = 'system:message:list', "
            "remark = '消息中心' WHERE menu_id = 352"
        )
    )
    for menu_id, name, permission, remark in (
        (378, "消息列表", "system:message:list", "消息列表权限"),
        (379, "消息查询", "system:message:query", "消息查询权限"),
        (380, "消息新增", "system:message:add", "消息新增权限"),
        (381, "消息编辑", "system:message:edit", "消息编辑权限"),
        (382, "消息删除", "system:message:remove", "消息删除权限"),
    ):
        op.execute(
            sa.text(
                "UPDATE menu SET menu_name = :name, perms = :permission, "
                "remark = :remark WHERE menu_id = :menu_id"
            ).bindparams(
                name=name,
                permission=permission,
                remark=remark,
                menu_id=menu_id,
            )
        )
    _clear_legacy_message_seeds()


def downgrade() -> None:
    """恢复历史表名和权限名称，保留迁移后的消息数据。"""
    for menu_id, name, permission, remark in (
        (378, "公告列表", "system:notice:list", "公告列表权限"),
        (379, "公告查询", "system:notice:query", "公告查询权限"),
        (380, "公告新增", "system:notice:add", "公告新增权限"),
        (381, "公告编辑", "system:notice:edit", "公告编辑权限"),
        (382, "公告删除", "system:notice:remove", "公告删除权限"),
    ):
        op.execute(
            sa.text(
                "UPDATE menu SET menu_name = :name, perms = :permission, "
                "remark = :remark WHERE menu_id = :menu_id"
            ).bindparams(
                name=name,
                permission=permission,
                remark=remark,
                menu_id=menu_id,
            )
        )
    op.execute(
        sa.text(
            "UPDATE menu SET menu_name = '通知公告', menu_path = 'notice', "
            "component = 'system/notice/index', perms = 'system:notice:list', "
            "remark = '通知公告' WHERE menu_id = 352"
        )
    )
    _rename_permissions(
        "system:message",
        "system:notice",
        ("list", "query", "add", "edit", "remove"),
        "公告",
    )

    for old_name, new_name in (
        ("ix_messages_message_title", "ix_notices_notice_title"),
        ("ix_messages_message_type", "ix_notices_notice_type"),
        ("ix_messages_status", "ix_notices_status"),
        ("ix_messages_publish_time", "ix_notices_publish_time"),
        ("ix_messages_create_by", "ix_notices_create_by"),
        ("ix_messages_tenant_id", "ix_notices_tenant_id"),
    ):
        _rename_index("messages", old_name, new_name)
    for old_name, new_name in (
        ("ix_message_recipients_user_id", "ix_notice_recipients_user_id"),
        ("ix_message_recipients_read_at", "ix_notice_recipients_read_at"),
    ):
        _rename_index("message_recipients", old_name, new_name)
    for old_name, new_name in (
        ("ix_message_deliveries_tenant_id", "ix_notification_deliveries_tenant_id"),
        ("ix_message_deliveries_message_id", "ix_notification_deliveries_notice_id"),
        ("ix_message_deliveries_user_id", "ix_notification_deliveries_user_id"),
        ("ix_message_deliveries_channel", "ix_notification_deliveries_channel"),
        ("ix_message_deliveries_status", "ix_notification_deliveries_status"),
        (
            "ix_message_deliveries_next_attempt_at",
            "ix_notification_deliveries_next_attempt_at",
        ),
        ("ix_message_deliveries_created_at", "ix_notification_deliveries_created_at"),
        ("ix_message_deliveries_lease_until", "ix_notification_deliveries_lease_until"),
    ):
        _rename_index("message_deliveries", old_name, new_name)

    _rename_table("message_deliveries", "notification_deliveries")
    _rename_column(
        "notification_deliveries",
        "message_id",
        "notice_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    _rename_table("message_recipients", "notice_recipients")
    _rename_column(
        "notice_recipients",
        "message_id",
        "notice_id",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )
    _rename_table("messages", "notices")
    _rename_column(
        "notices",
        "message_title",
        "notice_title",
        existing_type=sa.String(length=100),
        existing_nullable=False,
    )
    _rename_column(
        "notices",
        "message_type",
        "notice_type",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )
    _rename_column(
        "notices",
        "message_content",
        "notice_content",
        existing_type=sa.Text(),
        existing_nullable=False,
    )
