"""MySQL Server Configuration."""

from collections.abc import AsyncIterator
from typing import Union

from fastapi import Request
from loguru import logger
from config.env import settings
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker


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
    """MySQL Server Configuration."""

    DB_URL = (
        f"mysql+aiomysql://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}@"
        + f"{settings.MYSQL_HOST}:{settings.MYSQL_POST}/{settings.MYSQL_DATABASES}"
    )

    class MysqlError(Exception):
        """MySQL Server Error."""

    @staticmethod
    async def get_mysql_config() -> Union[tuple[AsyncEngine, sessionmaker]]:
        """Get MySQL Server Configuration."""
        logger.info("正在启动MySQL连接...")
        try:
            engine: AsyncEngine = create_async_engine(
                MysqlServe.DB_URL,
                echo=True,
                connect_args={"init_command": "SET time_zone = '+08:00'"},
            )
            logger.info("MySQL连接成功!")
            await MysqlServe.get_mysql_tables(engine)
            Session: sessionmaker = sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            return engine, Session
        except MysqlServe.MysqlError as e:
            logger.error(f"连接MySQL失败:{e}")

    @staticmethod
    async def get_mysql_tables(engine: AsyncEngine):
        """MySQL Server Configuration."""
        logger.info("正在获取MySQL表...")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("获取MySQL表成功!")
        except MysqlServe.MysqlError as e:
            logger.error(f"获取MySQL表失败:{e}")
