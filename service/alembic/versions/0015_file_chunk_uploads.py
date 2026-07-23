"""创建文件分片上传会话表。"""

import sqlalchemy as sa

from alembic import op

revision = "0015_file_chunk_uploads"
down_revision = "0014_tenant_operational_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "file_chunk_uploads",
        sa.Column("upload_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("original_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("total_size", sa.Integer(), nullable=False),
        sa.Column("total_chunks", sa.Integer(), nullable=False),
        sa.Column("received_chunks_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("upload_id"),
    )
    op.create_index(
        "ix_file_chunk_uploads_tenant_id", "file_chunk_uploads", ["tenant_id"]
    )
    op.create_index(
        "ix_file_chunk_uploads_created_by", "file_chunk_uploads", ["created_by"]
    )
    op.create_index(
        "ix_file_chunk_uploads_created_at", "file_chunk_uploads", ["created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_file_chunk_uploads_created_at", table_name="file_chunk_uploads")
    op.drop_index("ix_file_chunk_uploads_created_by", table_name="file_chunk_uploads")
    op.drop_index("ix_file_chunk_uploads_tenant_id", table_name="file_chunk_uploads")
    op.drop_table("file_chunk_uploads")
