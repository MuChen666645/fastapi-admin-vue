"""Redis."""

from fastapi import FastAPI
import redis.asyncio as aioredis
from redis import Redis
from loguru import logger
from config.env import settings


class RedisServe:
    """Redis."""

    class RedisError(Exception):
        """Redis error."""

    @classmethod
    async def get_redis_server(cls):
        """Get redis."""
        logger.info("正在启动Redis连接...")
        redis: Redis = await aioredis.from_url(
            url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_POST}",
            db=settings.REDIS_DB,
            encoding="utf-8",
            decode_responses=True,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
        )
        try:
            await redis.ping()
        except aioredis.AuthenticationError:
            logger.error("Redis用户名或密码错误!")
        except aioredis.TimeoutError:
            logger.error("Redis连接超时!")
        except RedisServe.RedisError as e:
            logger.error(f"Redis连接失败!{e}")
        logger.info("Redis连接成功!")
        return redis

    @classmethod
    async def close_redis_server(cls, app: FastAPI):
        """Close redis."""
        logger.info("正在关闭Redis连接...")
        if app.state.redis:
            await app.state.redis.close()
        logger.info("Redis连接已关闭!")
