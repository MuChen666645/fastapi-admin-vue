"""Rate limiting configuration tests."""

import anyio
import pytest

from config.env import settings
from config.rate_limit import limiter
from module_admin.service.user_service import UserService
from test.conftest import create_async_client


def _route_limits(endpoint_name: str):
    return [
        limit
        for route_name, limits in limiter._route_limits.items()
        if route_name.endswith(f".{endpoint_name}")
        for limit in limits
    ]


def test_rate_limit_defaults_support_admin_page_concurrency() -> None:
    assert settings.RATE_LIMIT_DEFAULT == "300/minute"
    assert limiter._storage_uri == (
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_POST}/{settings.REDIS_DB}"
    )
    assert limiter._storage_options == {
        "username": settings.REDIS_USERNAME,
        "password": settings.REDIS_PASSWORD,
    }
    default_limits = list(limiter._default_limits[0])
    assert len(default_limits) == 1
    assert default_limits[0].limit.amount == 300
    assert default_limits[0].limit.get_expiry() == 60


def test_sensitive_endpoints_use_stricter_limits() -> None:
    for endpoint_name in ("login_user", "login_user_by_phone"):
        limits = _route_limits(endpoint_name)
        assert len(limits) == 1
        assert limits[0].limit.amount == 10
        assert limits[0].limit.get_expiry() == 60

    for endpoint_name in ("get_captcha_img", "verify_captcha"):
        limits = _route_limits(endpoint_name)
        assert len(limits) == 1
        assert limits[0].limit.amount == 30
        assert limits[0].limit.get_expiry() == 60


def test_global_limit_allows_burst_requests() -> None:
    async def run() -> None:
        limiter.reset()
        limiter.enabled = True
        try:
            async with create_async_client() as client:
                responses = [await client.get("/openapi.json") for _ in range(5)]
            assert all(response.status_code == 200 for response in responses)
        finally:
            limiter.enabled = False
            limiter.reset()

    anyio.run(run)


def test_login_limit_rejects_excessive_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def login(*args, **kwargs):
        return {"token": "test-token"}

    async def run() -> None:
        monkeypatch.setattr(
            UserService,
            "get_user_by_username_services",
            login,
        )
        limiter.reset()
        limiter.enabled = True
        try:
            async with create_async_client() as client:
                responses = [
                    await client.post(
                        "/user/login/username",
                        data={
                            "username": "admin",
                            "password": "password",
                            "captcha_id": "captcha-id-1234567890",
                            "captcha": "1234",
                        },
                    )
                    for _ in range(11)
                ]
            assert all(response.status_code == 200 for response in responses[:10])
            assert responses[10].status_code == 429
        finally:
            limiter.enabled = False
            limiter.reset()

    anyio.run(run)
