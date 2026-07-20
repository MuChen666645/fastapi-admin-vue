import pytest
from pydantic import ValidationError

from config.env import Settings, _resolve_environment_file


def valid_shared_settings(**overrides) -> dict:
    values = {
        "APP_ENV": "staging",
        "DEBUG": False,
        "TITLE": "FastAPI Admin",
        "SUMMARY": "FastAPI admin service",
        "VERSION": "0.0.1",
        "OPENAPI_URL": "/openapi.json",
        "MYSQL_HOST": "mysql",
        "MYSQL_POST": 3306,
        "MYSQL_USERNAME": "app",
        "MYSQL_PASSWORD": "a-real-mysql-password",
        "MYSQL_DATABASES": "fastapi_admin",
        "TIMEZONE": "Asia/Shanghai",
        "REDIS_HOST": "redis",
        "REDIS_POST": 6379,
        "REDIS_DB": 0,
        "REDIS_PASSWORD": "a-real-redis-password",
        "REDIS_USERNAME": "default",
        "SECRET_KEY": "a-generated-secret-key-with-at-least-32-chars",
        "ACCESS_TOKEN_EXPIRE_MINUTES": 3600,
        "ADMIN_ROLE_CODE": "admin",
        "ACCESS_KEY_ID": "a-real-access-key-id",
        "ACCESSKEY_SECRET": "a-real-access-key-secret",
        "RATE_LIMIT_DEFAULT": "300/minute",
        "RATE_LIMIT_LOGIN": "10/minute",
        "RATE_LIMIT_CAPTCHA": "30/minute",
        "CAPTCHA_TTL_SECONDS": 300,
        "CAPTCHA_MAX_VERIFY_ATTEMPTS": 5,
        "LOGIN_MAX_FAILED_ATTEMPTS": 5,
        "LOGIN_IP_LOCK_SECONDS": 300,
        "READINESS_TIMEOUT_SECONDS": 5,
        "HOSTS": ["admin.example.com"],
        "TRUSTED_PROXIES": [],
        "ORIGINS": ["https://admin.example.com"],
        "MEDOTHS": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "HEADERS": ["Authorization", "Content-Type"],
        "CREDENTIALS": True,
    }
    values.update(overrides)
    return values


def test_development_profile_file_exists() -> None:
    assert _resolve_environment_file("development").name == ".env.development"


def test_development_profile_contains_runtime_settings() -> None:
    settings = Settings(_env_file=_resolve_environment_file("development"))

    assert settings.TITLE == "FastAPI Admin"
    assert settings.MYSQL_POST == 3306
    assert settings.REDIS_POST == 6379
    assert settings.RATE_LIMIT_DEFAULT == "300/minute"
    assert settings.CAPTCHA_TTL_SECONDS == 300
    assert settings.READINESS_TIMEOUT_SECONDS == 5


def test_shared_environment_rejects_placeholder_secrets() -> None:
    with pytest.raises(ValidationError, match="Generated non-placeholder secrets"):
        Settings(
            **valid_shared_settings(
                SECRET_KEY="REPLACE_WITH_A_RANDOM_STAGING_SECRET_AT_LEAST_32_CHARS"
            )
        )


def test_shared_environment_rejects_debug_and_wildcard_hosts() -> None:
    with pytest.raises(ValidationError, match="DEBUG must be false"):
        Settings(**valid_shared_settings(DEBUG=True))

    with pytest.raises(ValidationError, match="HOSTS, ORIGINS, and HEADERS"):
        Settings(**valid_shared_settings(HOSTS=["*"], ORIGINS=["*"]))
