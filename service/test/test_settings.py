import pytest
from pydantic import ValidationError

from config.env import Settings, _resolve_environment_file


def valid_shared_settings(**overrides) -> dict:
    values = {
        "APP_ENV": "staging",
        "DEBUG": False,
        "MYSQL_HOST": "mysql",
        "MYSQL_USERNAME": "app",
        "MYSQL_PASSWORD": "a-real-mysql-password",
        "MYSQL_DATABASES": "fastapi_admin",
        "REDIS_HOST": "redis",
        "REDIS_PASSWORD": "a-real-redis-password",
        "SECRET_KEY": "a-generated-secret-key-with-at-least-32-chars",
        "ACCESS_KEY_ID": "a-real-access-key-id",
        "ACCESSKEY_SECRET": "a-real-access-key-secret",
        "HOSTS": ["admin.example.com"],
        "ORIGINS": ["https://admin.example.com"],
    }
    values.update(overrides)
    return values


def test_development_profile_file_exists() -> None:
    assert _resolve_environment_file("development").name == ".env.development"


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
