"""Redis connection configuration."""

from fastapi import FastAPI
import redis.asyncio as aioredis
from redis.asyncio import Redis
from loguru import logger

from config.env import settings


class RedisServe:
    """Redis server configuration."""

    class RedisError(Exception):
        """Redis connection error."""

    @classmethod
    async def get_redis_server(cls):
        """Create a Redis client and fail startup if the connection is unusable."""
        logger.info("Starting Redis connection")
        redis: Redis = aioredis.from_url(
            url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_POST}",
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
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
        """Close Redis during application shutdown."""
        logger.info("Closing Redis connection")
        redis = getattr(app.state, "redis", None)
        if redis:
            close = getattr(redis, "aclose", None) or redis.close
            await close()
            app.state.redis = None
        logger.info("Redis connection closed")
