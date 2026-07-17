"""Apply database migrations, including the legacy schema baseline."""

import asyncio

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import command
from alembic.config import Config
from config.env import PROJECT_ROOT
from config.mysql_serve import MysqlServe


async def _database_state() -> tuple[bool, str | None]:
    """Return whether this is a legacy database and its Alembic version."""
    engine = create_async_engine(MysqlServe.DB_URL, pool_pre_ping=True)
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


def _alembic_config() -> Config:
    """Load the repository Alembic configuration."""
    return Config(str(PROJECT_ROOT / "alembic.ini"))


def main() -> None:
    """Baseline legacy installations and apply all pending migrations."""
    is_legacy, _ = asyncio.run(_database_state())
    config = _alembic_config()
    if is_legacy:
        command.stamp(config, "0001_initial_schema")
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
