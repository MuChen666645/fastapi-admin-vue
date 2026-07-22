"""创建初始 SQLModel 数据库结构。

Revision ID: 0001_initial_schema
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """创建首个应用版本的数据库结构快照。"""
    op.create_table(
        "dict_types",
        sa.Column("dict_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dict_name", sa.String(length=100), nullable=False),
        sa.Column("dict_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("dict_id"),
    )
    op.create_index("ix_dict_types_dict_name", "dict_types", ["dict_name"])
    op.create_index("ix_dict_types_status", "dict_types", ["status"])
    op.create_index(
        "ix_dict_types_dict_type", "dict_types", ["dict_type"], unique=True
    )

    op.create_table(
        "dict_data",
        sa.Column("dict_code", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("dict_sort", sa.Integer(), nullable=False),
        sa.Column("dict_label", sa.String(length=100), nullable=False),
        sa.Column("dict_value", sa.String(length=100), nullable=False),
        sa.Column("dict_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("dict_code"),
    )
    op.create_index("ix_dict_data_dict_type", "dict_data", ["dict_type"])
    op.create_index("ix_dict_data_status", "dict_data", ["status"])
    op.create_index("ix_dict_data_dict_label", "dict_data", ["dict_label"])

    op.create_table(
        "menu",
        sa.Column("menu_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("menu_name", sa.String(length=50), nullable=False),
        sa.Column("icon", sa.String(length=255), nullable=True),
        sa.Column("menu_path", sa.String(length=200), nullable=True),
        sa.Column("component", sa.String(length=200), nullable=True),
        sa.Column("is_hidden", sa.String(length=1), nullable=False),
        sa.Column("is_cache", sa.String(length=1), nullable=False),
        sa.Column("menu_type", sa.String(length=1), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=True),
        sa.Column("link_url", sa.String(length=200), nullable=True),
        sa.Column("perms", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["menu.menu_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("menu_id"),
        sa.UniqueConstraint("menu_name"),
    )

    op.create_table(
        "departments",
        sa.Column("dept_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("ancestors", sa.String(length=500), nullable=False),
        sa.Column("dept_name", sa.String(length=50), nullable=False),
        sa.Column("order_num", sa.Integer(), nullable=False),
        sa.Column("leader", sa.String(length=50), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["departments.dept_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("dept_id"),
    )
    op.create_index("ix_departments_status", "departments", ["status"])
    op.create_index("ix_departments_dept_name", "departments", ["dept_name"])
    op.create_index("ix_departments_parent_id", "departments", ["parent_id"])

    op.create_table(
        "posts",
        sa.Column("post_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_code", sa.String(length=64), nullable=False),
        sa.Column("post_name", sa.String(length=50), nullable=False),
        sa.Column("post_sort", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("post_id"),
    )
    op.create_unique_constraint("uq_posts_post_code", "posts", ["post_code"])
    op.create_index("ix_posts_status", "posts", ["status"])
    op.create_index("ix_posts_post_name", "posts", ["post_name"])

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=True),
        sa.Column("permission_type", sa.String(length=20), nullable=False),
        sa.Column("api_path", sa.String(length=200), nullable=True),
        sa.Column("api_method", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.Column("remark", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint("uq_permissions_code", "permissions", ["code"])

    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("update_time", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "role_menu",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["menu_id"], ["menu.menu_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "menu_id"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("create_time", sa.DateTime(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=11), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("dept_id", sa.Integer(), nullable=True),
        sa.Column("nickname", sa.String(length=50), nullable=True),
        sa.Column("sex", sa.String(length=255), nullable=True),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("update_time", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.ForeignKeyConstraint(["dept_id"], ["departments.dept_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_dept_id", "users", ["dept_id"])

    op.create_table(
        "login_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=1), nullable=False),
        sa.Column("message", sa.String(length=500), nullable=True),
        sa.Column("login_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_login_logs_login_time", "login_logs", ["login_time"])
    op.create_index("ix_login_logs_username", "login_logs", ["username"])
    op.create_index("ix_login_logs_user_id", "login_logs", ["user_id"])
    op.create_index("ix_login_logs_status", "login_logs", ["status"])

    op.create_table(
        "operation_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("operation_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_operation_logs_user_id", "operation_logs", ["user_id"])
    op.create_index(
        "ix_operation_logs_status_code", "operation_logs", ["status_code"]
    )
    op.create_index("ix_operation_logs_username", "operation_logs", ["username"])
    op.create_index("ix_operation_logs_path", "operation_logs", ["path"])
    op.create_index(
        "ix_operation_logs_operation_time", "operation_logs", ["operation_time"]
    )

    op.create_table(
        "exception_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("username", sa.String(length=50), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("exception_type", sa.String(length=200), nullable=False),
        sa.Column("exception_message", sa.String(length=2000), nullable=False),
        sa.Column("traceback", sa.Text(), nullable=True),
        sa.Column("exception_time", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_exception_logs_exception_type", "exception_logs", ["exception_type"]
    )
    op.create_index("ix_exception_logs_path", "exception_logs", ["path"])
    op.create_index(
        "ix_exception_logs_exception_time", "exception_logs", ["exception_time"]
    )
    op.create_index("ix_exception_logs_user_id", "exception_logs", ["user_id"])

    op.create_table(
        "user_post",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.post_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "post_id"),
    )

    op.create_table(
        "user_role",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )


def downgrade() -> None:
    """删除本版本迁移创建的数据库结构。"""
    for table_name in (
        "user_role",
        "user_post",
        "exception_logs",
        "operation_logs",
        "login_logs",
        "users",
        "role_menu",
        "roles",
        "permissions",
        "posts",
        "departments",
        "menu",
        "dict_data",
        "dict_types",
    ):
        op.drop_table(table_name)
