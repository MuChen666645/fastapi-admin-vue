"""Application settings and environment-file selection."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EnvironmentName = Literal["development", "staging", "production"]
ENVIRONMENT_NAMES = {"development", "staging", "production"}
REQUIRED_ENVIRONMENT_VARIABLES = {
    "MYSQL_HOST",
    "MYSQL_USERNAME",
    "MYSQL_PASSWORD",
    "MYSQL_DATABASES",
    "REDIS_HOST",
    "SECRET_KEY",
    "ACCESS_KEY_ID",
    "ACCESSKEY_SECRET",
}
PLACEHOLDER_SECRET_MARKERS = (
    "change-me",
    "change_me",
    "replace",
    "your_",
    "example",
    "dev-only",
    "fastapi",
)


def _resolve_environment() -> EnvironmentName:
    raw_environment = os.getenv("APP_ENV", "development").strip().lower()
    if raw_environment not in ENVIRONMENT_NAMES:
        supported = ", ".join(sorted(ENVIRONMENT_NAMES))
        raise RuntimeError(
            f"APP_ENV must be one of {supported}; got {raw_environment!r}"
        )
    return raw_environment  # type: ignore[return-value]


def _resolve_environment_file(environment: EnvironmentName) -> Path:
    environment_file = PROJECT_ROOT / f".env.{environment}"
    if environment_file.exists():
        return environment_file
    if environment == "development":
        legacy_file = PROJECT_ROOT / ".env"
        if legacy_file.exists():
            return legacy_file
    raise RuntimeError(
        f"Missing configuration file {environment_file}. "
        f"Copy the matching .example file before starting the service."
    )


class Settings(BaseSettings):
    """Typed application configuration."""

    class HttpResponses(BaseModel):
        """Default response metadata."""

        code: int
        message: str
        data: Any

    APP_ENV: EnvironmentName = "development"

    # FastAPI
    DEBUG: bool = False
    TITLE: str = "FastAPI Admin"
    SUMMARY: str = "FastAPI, SQLModel, MySQL and Redis admin service."
    VERSION: str = "0.0.1"
    OPENAPI_URL: str = "/openapi.json"
    RESPONSES: dict[int, dict[str, str | type]] = {
        422: {"description": "Validation Error", "model": HttpResponses},
        401: {"description": "Token Error", "model": HttpResponses},
    }

    # MySQL
    MYSQL_HOST: str = Field(min_length=1)
    MYSQL_POST: int = Field(default=3306, gt=0, le=65535)
    MYSQL_USERNAME: str = Field(min_length=1)
    MYSQL_PASSWORD: str = Field(min_length=1)
    MYSQL_DATABASES: str = Field(min_length=1)
    TIMEZONE: str = "Asia/Shanghai"

    # Redis
    REDIS_HOST: str = Field(min_length=1)
    REDIS_POST: int = Field(default=6379, gt=0, le=65535)
    REDIS_PASSWORD: str = ""
    REDIS_USERNAME: str = ""
    REDIS_DB: int = Field(default=0, ge=0)

    # Token and RBAC
    SECRET_KEY: str = Field(min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=3600, gt=0)
    ADMIN_ROLE_CODE: str = Field(default="admin", min_length=1)

    # Rate limit and verification
    RATE_LIMIT_DEFAULT: str = "300/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_CAPTCHA: str = "30/minute"
    CAPTCHA_TTL_SECONDS: int = Field(default=300, gt=0)
    CAPTCHA_MAX_VERIFY_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_MAX_FAILED_ATTEMPTS: int = Field(default=5, gt=0)
    LOGIN_IP_LOCK_SECONDS: int = Field(default=300, gt=0)

    # Aliyun OSS
    ACCESS_KEY_ID: str = Field(min_length=1)
    ACCESSKEY_SECRET: str = Field(min_length=1)

    # Network policy
    HOSTS: list[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    TRUSTED_PROXIES: list[str] = Field(default_factory=list)
    ORIGINS: list[str] = Field(default_factory=list)
    MEDOTHS: list[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "DELETE"]
    )
    HEADERS: list[str] = Field(default_factory=lambda: ["*"])
    CREDENTIALS: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_environment_security(self) -> "Settings":
        """Reject development defaults in shared environments."""
        if self.APP_ENV == "development":
            return self

        secret_values = {
            "SECRET_KEY": self.SECRET_KEY,
            "MYSQL_PASSWORD": self.MYSQL_PASSWORD,
            "REDIS_PASSWORD": self.REDIS_PASSWORD,
            "ACCESS_KEY_ID": self.ACCESS_KEY_ID,
            "ACCESSKEY_SECRET": self.ACCESSKEY_SECRET,
        }
        placeholder_values = [
            name
            for name, value in secret_values.items()
            if any(
                marker in value.casefold() for marker in PLACEHOLDER_SECRET_MARKERS
            )
        ]
        if len(self.SECRET_KEY) < 32 or placeholder_values:
            fields = ", ".join(placeholder_values or ["SECRET_KEY"])
            raise ValueError(
                "Generated non-placeholder secrets are required outside "
                f"development: {fields}"
            )
        if self.DEBUG:
            raise ValueError("DEBUG must be false outside development")
        if "*" in self.HOSTS or "*" in self.ORIGINS or "*" in self.HEADERS:
            raise ValueError(
                "HOSTS, ORIGINS, and HEADERS must be restricted outside development"
            )
        if not self.REDIS_PASSWORD:
            raise ValueError("REDIS_PASSWORD is required outside development")
        return self


@lru_cache
def get_settings() -> Settings:
    """Load settings using APP_ENV and the matching environment file."""
    environment = _resolve_environment()
    try:
        environment_file = _resolve_environment_file(environment)
    except RuntimeError:
        if not REQUIRED_ENVIRONMENT_VARIABLES.issubset(os.environ):
            raise
        environment_file = None
    return Settings(_env_file=environment_file)


settings = get_settings()
