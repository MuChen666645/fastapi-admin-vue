"""Redis 连接配置。"""

import redis.asyncio as aioredis
from fastapi import FastAPI
from loguru import logger
from redis.asyncio import Redis

from config.env import Settings, settings


class RedisServe:
    """Redis 服务配置。"""

    class RedisError(Exception):
        """Redis 连接错误。"""

    @classmethod
    async def get_redis_server(cls, app_settings: Settings | None = None):
        """创建 Redis 客户端，连接不可用时让应用启动失败。"""
        app_settings = app_settings or settings
        logger.info("Starting Redis connection")
        redis: Redis = aioredis.from_url(
            url=f"redis://{app_settings.REDIS_HOST}:{app_settings.REDIS_POST}",
            db=app_settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
            username=app_settings.REDIS_USERNAME,
            password=app_settings.REDIS_PASSWORD,
        )
        try:
            await redis.ping()
        except Exception as exc:
            await redis.aclose()
            logger.exception("Redis connection failed")
            raise cls.RedisError("Redis connection failed") from exc
        logger.info("Redis connection ready")
        return redis

    @classmethod
    async def close_redis_server(cls, app: FastAPI):
        """应用关闭时释放 Redis 连接。"""
        logger.info("Closing Redis connection")
        redis = getattr(app.state, "redis", None)
        if redis:
            close = getattr(redis, "aclose", None) or redis.close
            await close()
            app.state.redis = None
        logger.info("Redis connection closed")
