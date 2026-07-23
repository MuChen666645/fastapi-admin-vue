"""MySQL 连接和请求会话配置。"""

import shutil
from collections.abc import AsyncIterator
from typing import Union

from fastapi import Request
from loguru import logger
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.env import Settings, settings


async def bind_request_mysql_session(request: Request) -> AsyncIterator[None]:
    """为当前 HTTP 请求绑定一个数据库会话。"""
    session_factory = request.app.state.mysql_session_factory
    async with session_factory() as session:
        request.state.mysql = session
        try:
            yield
            await session.commit()
        except BaseException:
            await session.rollback()
            pending_chunk_dirs = getattr(request.state, "pending_chunk_dirs", [])
            for upload_id, app_settings in reversed(pending_chunk_dirs):
                try:
                    from module_admin.service.file_service import FileService

                    shutil.rmtree(
                        FileService._chunk_dir(upload_id, app_settings),
                        ignore_errors=True,
                    )
                except Exception:
                    logger.exception(
                        "数据库回滚后的分片目录补偿清理失败",
                        upload_id=upload_id,
                    )
            pending = getattr(request.state, "pending_storage_objects", [])
            if pending:
                from module_admin.service.file_service import FileService

                for metadata, app_settings in reversed(pending):
                    try:
                        await FileService.delete_stored_file(metadata, app_settings)
                    except Exception:
                        logger.exception(
                            "数据库回滚后的文件补偿清理失败",
                            storage_key=metadata.storage_key,
                        )
            raise
        finally:
            request.state.pending_chunk_dirs = []
            request.state.pending_storage_objects = []
            request.state.mysql = None


class MysqlServe:
    """MySQL 服务配置。"""

    class MysqlError(Exception):
        """MySQL 连接错误。"""

    @staticmethod
    def get_db_url(app_settings: Settings | None = None) -> URL:
        """根据应用配置构造 MySQL 连接地址。"""
        app_settings = app_settings or settings
        return URL.create(
            drivername="mysql+aiomysql",
            username=app_settings.MYSQL_USERNAME,
            password=app_settings.MYSQL_PASSWORD,
            host=app_settings.MYSQL_HOST,
            port=app_settings.MYSQL_POST,
            database=app_settings.MYSQL_DATABASES,
        )

    @staticmethod
    async def get_mysql_config(
        app_settings: Settings | None = None,
    ) -> Union[tuple[AsyncEngine, sessionmaker]]:
        """创建并校验应用数据库引擎。

        数据库结构变更不在启动阶段执行，由 Alembic 管理，避免多实例并发执行 DDL。
        """
        app_settings = app_settings or settings
        logger.info("Starting MySQL connection")
        engine: AsyncEngine | None = None
        try:
            engine = create_async_engine(
                MysqlServe.get_db_url(app_settings),
                echo=app_settings.DEBUG,
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
