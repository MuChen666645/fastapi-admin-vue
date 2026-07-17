"""MySQL connection and request-session configuration."""

from collections.abc import AsyncIterator
from typing import Union

from fastapi import Request
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.env import settings


async def bind_request_mysql_session(request: Request) -> AsyncIterator[None]:
    """Bind one database session to the current HTTP request."""
    session_factory = request.app.state.mysql_session_factory
    async with session_factory() as session:
        request.state.mysql = session
        try:
            yield
            await session.commit()
        except BaseException:
            await session.rollback()
            raise
        finally:
            request.state.mysql = None


class MysqlServe:
    """MySQL server configuration."""

    DB_URL = (
        f"mysql+aiomysql://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}@"
        f"{settings.MYSQL_HOST}:{settings.MYSQL_POST}/{settings.MYSQL_DATABASES}"
    )

    class MysqlError(Exception):
        """MySQL server error."""

    @staticmethod
    async def get_mysql_config() -> Union[tuple[AsyncEngine, sessionmaker]]:
        """Create and validate the application engine.

        Schema changes are intentionally excluded from startup. They are managed
        by Alembic so multiple application instances cannot race on DDL.
        """
        logger.info("Starting MySQL connection")
        engine: AsyncEngine | None = None
        try:
            engine = create_async_engine(
                MysqlServe.DB_URL,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                connect_args={"init_command": "SET time_zone = '+08:00'"},
            )
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            logger.info("MySQL connection ready")
            session_factory = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            return engine, session_factory
        except Exception as exc:
            if engine is not None:
                await engine.dispose()
            logger.exception("MySQL connection failed")
            raise MysqlServe.MysqlError("MySQL connection failed") from exc
