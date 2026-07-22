"""基于共享 Redis 的限流配置。"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from config.env import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
    storage_uri=(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_POST}/{settings.REDIS_DB}"
    ),
    storage_options={
        "username": settings.REDIS_USERNAME,
        "password": settings.REDIS_PASSWORD,
    },
)
