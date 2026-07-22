"""执行数据库迁移，并处理旧版数据库基线。"""

import asyncio

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError

from alembic import command
from alembic.config import Config
from config.env import PROJECT_ROOT
from config.mysql_serve import MysqlServe


async def _database_state() -> tuple[bool, str | None]:
    """返回数据库是否为旧版结构以及当前 Alembic 版本。"""
    engine = create_async_engine(MysqlServe.get_db_url(), pool_pre_ping=True)
    try:
        async with engine.connect() as connection:
            tables = await connection.run_sync(
                lambda sync_connection: {
                    table_name
                    for table_name in inspect(sync_connection).get_table_names()
                }
            )
            version = None
            if "alembic_version" in tables:
                version = (
                    await connection.execute(
                        text("SELECT version_num FROM alembic_version LIMIT 1")
                    )
                ).scalar_one_or_none()
            return "users" in tables and version is None, version
    finally:
        await engine.dispose()


async def _ensure_alembic_version_capacity() -> None:
    """扩大 Alembic 版本列，兼容历史默认的 VARCHAR(32)。"""
    engine = create_async_engine(MysqlServe.get_db_url(), pool_pre_ping=True)
    try:
        async with engine.begin() as connection:
            tables = await connection.run_sync(
                lambda sync_connection: set(
                    inspect(sync_connection).get_table_names()
                )
            )
            if "alembic_version" in tables:
                await connection.execute(
                    text(
                        "ALTER TABLE alembic_version "
                        "MODIFY COLUMN version_num VARCHAR(64) NOT NULL"
                    )
                )
            else:
                await connection.execute(
                    text(
                        "CREATE TABLE alembic_version ("
                        "version_num VARCHAR(64) NOT NULL, "
                        "CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"
                    )
                )
    finally:
        await engine.dispose()


def _alembic_config() -> Config:
    """加载项目根目录下的 Alembic 配置。"""
    return Config(str(PROJECT_ROOT / "alembic.ini"))


def main() -> None:
    """为旧版安装标记基线，并应用全部待执行迁移。"""
    try:
        is_legacy, _ = asyncio.run(_database_state())
    except OperationalError as exc:
        if "1045" in str(exc):
            raise SystemExit(
                "MySQL login was rejected (1045). The credentials in the "
                "persistent mysql-data volume do not match MYSQL_PASSWORD "
                "or MYSQL_USERNAME in the selected env file. Use the original "
                "password to rotate the account, or recreate the development "
                "volume only after backing up required data."
            ) from None
        raise
    config = _alembic_config()
    if is_legacy:
        command.stamp(config, "0001_initial_schema")
    asyncio.run(_ensure_alembic_version_capacity())
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
