"""异步 SQLModel 元数据的 Alembic 环境。"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from alembic import context
from config.mysql_serve import MysqlServe
from module_admin.entity.do import dictionary_do as _dictionary_do
from module_admin.entity.do import file_do as _file_do
from module_admin.entity.do import job_do as _job_do
from module_admin.entity.do import log_do as _log_do
from module_admin.entity.do import menu_do as _menu_do
from module_admin.entity.do import notice_do as _notice_do
from module_admin.entity.do import organization_do as _organization_do
from module_admin.entity.do import permission_do as _permission_do
from module_admin.entity.do import role_do as _role_do
from module_admin.entity.do import system_config_do as _system_config_do
from module_admin.entity.do import user_do as _user_do

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """不创建数据库连接，使用离线模式生成并执行迁移。"""
    context.configure(
        url=MysqlServe.get_db_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """使用同步连接配置 Alembic 并执行迁移。"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """为迁移命令创建短生命周期的异步引擎。"""
    connectable = create_async_engine(
        MysqlServe.get_db_url(),
        poolclass=pool.NullPool,
        connect_args={"init_command": "SET time_zone = '+08:00'"},
    )
    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """通过在线异步数据库连接执行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
