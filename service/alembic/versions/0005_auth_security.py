"""增加密码生命周期、MFA 和密码找回数据结构。"""

import sqlalchemy as sa

from alembic import op

revision = "0005_auth_security"
down_revision = "0004_role_code_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """为用户账号增加安全状态和密码找回表。"""
    op.add_column(
        "users",
        sa.Column("password_changed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "must_change_password",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "mfa_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("mfa_secret_encrypted", sa.Text(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("mfa_recovery_codes_encrypted", sa.Text(), nullable=True),
    )
    op.create_table(
        "user_password_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_password_history_user_id",
        "user_password_history",
        ["user_id"],
    )
    op.create_index(
        "ix_user_password_history_created_at",
        "user_password_history",
        ["created_at"],
    )
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=10), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_password_reset_tokens_user_id",
        "password_reset_tokens",
        ["user_id"],
    )
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
    )
    op.create_index(
        "ix_password_reset_tokens_expires_at",
        "password_reset_tokens",
        ["expires_at"],
    )


def downgrade() -> None:
    """删除密码生命周期、MFA 和密码找回结构。"""
    op.drop_index(
        "ix_password_reset_tokens_expires_at",
        table_name="password_reset_tokens",
    )
    op.drop_index(
        "ix_password_reset_tokens_token_hash",
        table_name="password_reset_tokens",
    )
    op.drop_index(
        "ix_password_reset_tokens_user_id",
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")
    op.drop_index(
        "ix_user_password_history_created_at",
        table_name="user_password_history",
    )
    op.drop_index(
        "ix_user_password_history_user_id",
        table_name="user_password_history",
    )
    op.drop_table("user_password_history")
    for column in (
        "mfa_recovery_codes_encrypted",
        "mfa_secret_encrypted",
        "mfa_enabled",
        "must_change_password",
        "password_changed_at",
    ):
        op.drop_column("users", column)
