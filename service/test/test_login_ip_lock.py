"""Login IP lockout tests."""

from test.conftest import app, create_async_client
from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException

from config.env import settings
from module_admin.dao.user_dao import UserDao
from module_admin.entity.dto.user_dto import (
    LoginUserRequestByPhoneDto,
    LoginUserRequestByUsernameDto,
)
from module_admin.service.login_security_service import LoginSecurityService
from module_admin.service.user_service import UserService
from utils.fastapi_admin import FastApiAdmin


def make_request(ip_address: str = "198.51.100.20") -> SimpleNamespace:
    return SimpleNamespace(
        app=app,
        client=SimpleNamespace(host=ip_address),
        headers={"user-agent": "pytest"},
        state=SimpleNamespace(),
    )


def test_login_ip_lock_defaults() -> None:
    assert settings.LOGIN_MAX_FAILED_ATTEMPTS == 5
    assert settings.LOGIN_IP_LOCK_SECONDS == 300


def test_fifth_password_failure_locks_ip() -> None:
    async def run() -> None:
        request = make_request()
        for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS - 1):
            await LoginSecurityService.record_password_failure(request)

        with pytest.raises(HTTPException) as exception:
            await LoginSecurityService.record_password_failure(request)
        assert exception.value.status_code == 429
        assert exception.value.headers == {"Retry-After": "300"}

        with pytest.raises(HTTPException) as locked_exception:
            await LoginSecurityService.ensure_ip_allowed(request)
        assert locked_exception.value.status_code == 429

    anyio.run(run)


def test_correct_password_clears_unlocked_failure_counter() -> None:
    async def run() -> None:
        request = make_request()
        for _ in range(2):
            await LoginSecurityService.record_password_failure(request)
        await LoginSecurityService.clear_password_failures(request)

        for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS - 1):
            await LoginSecurityService.record_password_failure(request)
        await LoginSecurityService.ensure_ip_allowed(request)

    anyio.run(run)


def test_ip_lock_is_shared_by_username_and_phone_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        user = SimpleNamespace(
            id=2,
            username="operator",
            phone="13800138000",
            password="hashed-password",
        )
        phone_query_count = 0

        async def get_user_by_username(*args, **kwargs):
            return user

        async def get_user_by_phone(*args, **kwargs):
            nonlocal phone_query_count
            phone_query_count += 1
            return user

        async def record_login(*args, **kwargs):
            return None

        monkeypatch.setattr(UserDao, "get_user_by_username", get_user_by_username)
        monkeypatch.setattr(UserDao, "get_user_by_phone", get_user_by_phone)
        monkeypatch.setattr(FastApiAdmin, "verify_password", lambda *args: False)
        monkeypatch.setattr(UserService, "_record_login", record_login)

        username_login = LoginUserRequestByUsernameDto(
            username="operator",
            password="wrong-password",
            captcha_id="captcha-id-1234567890",
            captcha="1234",
        )
        async with create_async_client() as client:
            for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS - 1):
                response = await client.post(
                    "/api/v1/user/login/username",
                    data=username_login.model_dump(),
                )
                assert response.status_code == 401

            lock_response = await client.post(
                "/api/v1/user/login/username",
                data=username_login.model_dump(),
            )
            assert lock_response.status_code == 429
            assert lock_response.headers["retry-after"] == "300"

            phone_login = LoginUserRequestByPhoneDto(
                phone="13800138000",
                password="correct-password",
                captcha_id="captcha-id-1234567890",
                captcha="1234",
            )
            phone_response = await client.post(
                "/api/v1/user/login/phone",
                data=phone_login.model_dump(),
            )
            assert phone_response.status_code == 429
        assert phone_query_count == 0

    anyio.run(run)
