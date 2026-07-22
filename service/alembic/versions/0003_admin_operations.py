"""新增文件管理、系统参数、通知公告和定时任务表。"""

import sqlalchemy as sa

from alembic import op

revision = "0003_admin_operations"
down_revision = "0002_role_data_scope"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建管理功能数据表和内置权限。"""
    op.create_table(
        "file_metadata",
        sa.Column("file_id", sa.String(length=36), nullable=False),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("storage_backend", sa.String(length=20), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("file_id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_file_metadata_storage_key", "file_metadata", ["storage_key"])
    op.create_index("ix_file_metadata_checksum", "file_metadata", ["checksum"])
    op.create_index("ix_file_metadata_created_by", "file_metadata", ["created_by"])
    op.create_index("ix_file_metadata_create_time", "file_metadata", ["create_time"])

    op.create_table(
        "system_configs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("config_name", sa.String(length=100), nullable=False),
        sa.Column("config_key", sa.String(length=100), nullable=False),
        sa.Column("config_value", sa.Text(), nullable=True),
        sa.Column("config_type", sa.String(length=20), nullable=False),
        sa.Column("is_builtin", sa.Boolean(), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_key"),
    )
    op.create_index("ix_system_configs_config_name", "system_configs", ["config_name"])
    op.create_index("ix_system_configs_config_key", "system_configs", ["config_key"])
    op.create_index("ix_system_configs_config_type", "system_configs", ["config_type"])
    op.create_index("ix_system_configs_is_builtin", "system_configs", ["is_builtin"])

    op.create_table(
        "notices",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("notice_title", sa.String(length=100), nullable=False),
        sa.Column("notice_type", sa.String(length=20), nullable=False),
        sa.Column("notice_content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("publish_time", sa.DateTime(), nullable=True),
        sa.Column("create_by", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["create_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notices_notice_title", "notices", ["notice_title"])
    op.create_index("ix_notices_notice_type", "notices", ["notice_type"])
    op.create_index("ix_notices_status", "notices", ["status"])
    op.create_index("ix_notices_publish_time", "notices", ["publish_time"])
    op.create_index("ix_notices_create_by", "notices", ["create_by"])

    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_name", sa.String(length=100), nullable=False),
        sa.Column("job_key", sa.String(length=100), nullable=False),
        sa.Column("task_name", sa.String(length=200), nullable=False),
        sa.Column("cron_expression", sa.String(length=100), nullable=False),
        sa.Column("args_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("last_run_time", sa.DateTime(), nullable=True),
        sa.Column("next_run_time", sa.DateTime(), nullable=True),
        sa.Column("last_status", sa.String(length=20), nullable=True),
        sa.Column("last_message", sa.Text(), nullable=True),
        sa.Column("create_by", sa.Integer(), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["create_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_key"),
    )
    op.create_index("ix_scheduled_jobs_job_name", "scheduled_jobs", ["job_name"])
    op.create_index("ix_scheduled_jobs_job_key", "scheduled_jobs", ["job_key"])
    op.create_index("ix_scheduled_jobs_task_name", "scheduled_jobs", ["task_name"])
    op.create_index("ix_scheduled_jobs_status", "scheduled_jobs", ["status"])
    op.create_index("ix_scheduled_jobs_create_by", "scheduled_jobs", ["create_by"])

    op.create_table(
        "job_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("task_name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["scheduled_jobs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_logs_job_id", "job_logs", ["job_id"])
    op.create_index("ix_job_logs_task_name", "job_logs", ["task_name"])
    op.create_index("ix_job_logs_status", "job_logs", ["status"])
    op.create_index("ix_job_logs_start_time", "job_logs", ["start_time"])

    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO permissions
                (name, code, module, permission_type, api_path, api_method,
                 status, create_time, update_time, remark)
            VALUES
                ('File upload', 'system:file:upload', 'system', 'button', '/file/upload', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File upload'),
                ('File download', 'system:file:download', 'system', 'button', '/file/download/{file_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File download'),
                ('File delete', 'system:file:remove', 'system', 'button', '/file/{file_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File delete'),
                ('Config list', 'system:config:list', 'system', 'button', '/config/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config list'),
                ('Config query', 'system:config:query', 'system', 'button', '/config/{config_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config query'),
                ('Config add', 'system:config:add', 'system', 'button', '/config/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config add'),
                ('Config edit', 'system:config:edit', 'system', 'button', '/config/{config_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config edit'),
                ('Config delete', 'system:config:remove', 'system', 'button', '/config/{config_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config delete'),
                ('Notice list', 'system:notice:list', 'system', 'button', '/notice/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice list'),
                ('Notice query', 'system:notice:query', 'system', 'button', '/notice/{notice_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice query'),
                ('Notice add', 'system:notice:add', 'system', 'button', '/notice/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice add'),
                ('Notice edit', 'system:notice:edit', 'system', 'button', '/notice/{notice_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice edit'),
                ('Notice delete', 'system:notice:remove', 'system', 'button', '/notice/{notice_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice delete'),
                ('Job list', 'monitor:job:list', 'monitor', 'button', '/job/list', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job list'),
                ('Job query', 'monitor:job:query', 'monitor', 'button', '/job/{job_id}', 'GET', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job query'),
                ('Job add', 'monitor:job:add', 'monitor', 'button', '/job/add', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job add'),
                ('Job edit', 'monitor:job:edit', 'monitor', 'button', '/job/{job_id}', 'PUT', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job edit'),
                ('Job delete', 'monitor:job:remove', 'monitor', 'button', '/job/{job_id}', 'DELETE', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job delete'),
                ('Job run', 'monitor:job:run', 'monitor', 'button', '/job/{job_id}/run', 'POST', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job run')
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO menu
                (menu_id, parent_id, menu_name, icon, menu_path, component,
                 is_hidden, is_cache, menu_type, sort, link_url, perms, status,
                 create_time, update_time, remark)
            VALUES
                (350, 2, 'File Storage', '#', 'file', 'system/file/index', '0', '1', 'C', 7, NULL, 'system:file:upload', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File storage'),
                (351, 2, 'System Config', '#', 'config', 'system/config/index', '0', '1', 'C', 8, NULL, 'system:config:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System config'),
                (352, 2, 'System Notice', '#', 'notice', 'system/notice/index', '0', '1', 'C', 9, NULL, 'system:notice:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'System notice'),
                (360, 200, 'Scheduled Jobs', '#', 'job', 'monitor/job/index', '0', '1', 'C', 3, NULL, 'monitor:job:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Scheduled jobs'),
                (370, 350, 'File Upload', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:file:upload', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File upload'),
                (371, 350, 'File Download', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:file:download', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File download'),
                (372, 350, 'File Delete', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:file:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'File delete'),
                (373, 351, 'Config List', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:config:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Config list'),
                (374, 351, 'Config Query', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:config:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Config query'),
                (375, 351, 'Config Add', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:config:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Config add'),
                (376, 351, 'Config Edit', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:config:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Config edit'),
                (377, 351, 'Config Delete', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:config:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Config delete'),
                (378, 352, 'Notice List', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'system:notice:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice list'),
                (379, 352, 'Notice Query', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'system:notice:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice query'),
                (380, 352, 'Notice Add', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'system:notice:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice add'),
                (381, 352, 'Notice Edit', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'system:notice:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice edit'),
                (382, 352, 'Notice Delete', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'system:notice:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Notice delete'),
                (383, 360, 'Job List', NULL, NULL, NULL, '0', '0', 'F', 1, NULL, 'monitor:job:list', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job list'),
                (384, 360, 'Job Query', NULL, NULL, NULL, '0', '0', 'F', 2, NULL, 'monitor:job:query', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job query'),
                (385, 360, 'Job Add', NULL, NULL, NULL, '0', '0', 'F', 3, NULL, 'monitor:job:add', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job add'),
                (386, 360, 'Job Edit', NULL, NULL, NULL, '0', '0', 'F', 4, NULL, 'monitor:job:edit', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job edit'),
                (387, 360, 'Job Delete', NULL, NULL, NULL, '0', '0', 'F', 5, NULL, 'monitor:job:remove', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job delete'),
                (388, 360, 'Job Run', NULL, NULL, NULL, '0', '0', 'F', 6, NULL, 'monitor:job:run', '1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'Job run')
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO role_menu (role_id, menu_id)
            SELECT 1, menu_id FROM menu WHERE menu_id BETWEEN 350 AND 388
            """
        )
    )


def downgrade() -> None:
    """删除管理功能数据表。"""
    op.drop_index("ix_job_logs_start_time", table_name="job_logs")
    op.drop_index("ix_job_logs_status", table_name="job_logs")
    op.drop_index("ix_job_logs_task_name", table_name="job_logs")
    op.drop_index("ix_job_logs_job_id", table_name="job_logs")
    op.drop_table("job_logs")
    op.drop_index("ix_scheduled_jobs_create_by", table_name="scheduled_jobs")
    op.drop_index("ix_scheduled_jobs_status", table_name="scheduled_jobs")
    op.drop_index("ix_scheduled_jobs_task_name", table_name="scheduled_jobs")
    op.drop_index("ix_scheduled_jobs_job_key", table_name="scheduled_jobs")
    op.drop_index("ix_scheduled_jobs_job_name", table_name="scheduled_jobs")
    op.drop_table("scheduled_jobs")
    op.drop_index("ix_notices_create_by", table_name="notices")
    op.drop_index("ix_notices_publish_time", table_name="notices")
    op.drop_index("ix_notices_status", table_name="notices")
    op.drop_index("ix_notices_notice_type", table_name="notices")
    op.drop_index("ix_notices_notice_title", table_name="notices")
    op.drop_table("notices")
    op.drop_index("ix_system_configs_is_builtin", table_name="system_configs")
    op.drop_index("ix_system_configs_config_type", table_name="system_configs")
    op.drop_index("ix_system_configs_config_key", table_name="system_configs")
    op.drop_index("ix_system_configs_config_name", table_name="system_configs")
    op.drop_table("system_configs")
    op.drop_index("ix_file_metadata_create_time", table_name="file_metadata")
    op.drop_index("ix_file_metadata_created_by", table_name="file_metadata")
    op.drop_index("ix_file_metadata_checksum", table_name="file_metadata")
    op.drop_index("ix_file_metadata_storage_key", table_name="file_metadata")
    op.drop_table("file_metadata")
