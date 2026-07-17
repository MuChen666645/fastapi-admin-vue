"""环境变量配置."""

from functools import lru_cache
from dataclasses import field
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
from pydantic import BaseModel, Field



# 创建Settings对象
class Settings(BaseSettings):
    """Settings对象."""

    class HttpResponses(BaseModel):
        """默认响应对象."""

        code: int
        message: str
        data: Any

    # fastapi
    DEBUG: bool = True
    TITLE: str = "FastAPI Admin"
    SUMMARY: str = (
        "FastAPI Admin 是一个基于 FastAPI、SQLModel、MySQL 和 Redis 构建的"
        "后台管理系统服务端，提供用户管理、角色权限、菜单管理、验证码、JWT "
        "鉴权、统一响应、日志记录和接口限流等基础能力。"
    )
    VERSION: str = "0.0.1"
    OPENAPI_URL: str = "/openapi.json"
    RESPONSES: dict[int, dict[str, str | type]] = {
        422: {"description": "Validation Error", "model": HttpResponses},
        401: {"description": "Token Error", "model": HttpResponses},
    }
    # MySQL
    MYSQL_HOST: str = field()
    MYSQL_POST: int = field()
    MYSQL_USERNAME: str = field()
    MYSQL_PASSWORD: str = field()
    MYSQL_DATABASES: str = field()
    TIMEZONE: str = field()
    # Redis
    REDIS_HOST: str = field()
    REDIS_POST: int = field()
    REDIS_PASSWORD: str = field()
    REDIS_USERNAME: str = field()
    REDIS_DB: int = field()
    # Token
    SECRET_KEY: str = "LqiiMUYZdhxFFWcK6V5QZzQGbbqo9_G-dAZnnMyoCBenCMToHqkrxOQC89ydRz3p"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    # RBAC
    ADMIN_ROLE_CODE: str = "admin"
    # Rate limit
    RATE_LIMIT_DEFAULT: str = "300/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_CAPTCHA: str = "30/minute"
    CAPTCHA_TTL_SECONDS: int = Field(default=300, gt=0)
    CAPTCHA_MAX_VERIFY_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_MAX_FAILED_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_IP_LOCK_SECONDS: int = Field(default=300, gt=0)
    # aliyun
    ACCESS_KEY_ID: str = field()
    ACCESSKEY_SECRET: str = field()
    # Host
    HOSTS: list[str] = field(default_factory=lambda: ["*"])
    TRUSTED_PROXIES: list[str] = field(default_factory=list)
    ORIGINS: list[str] = field(default_factory=lambda: ["*"])
    MEDOTHS: list[str] = field(default_factory=lambda: ["*"])
    HEADERS: list[str] = field(default_factory=lambda: ["*"])
    CREDENTIALS: bool = False

    # 读取环境变量
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env"
    )


@lru_cache
def get_settings():
    """使用lru_cache只创建一次Settings对象.

    Returns:
        Settings: Settings对象
    """
    return Settings()


settings = get_settings()
