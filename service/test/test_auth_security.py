import time
from test.conftest import app
from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.service.login_security_service import LoginSecurityService
from module_admin.service.mfa_service import MfaService
from module_admin.service.password_policy import PasswordPolicyError, validate_password


class FakeUserSession:
    def __init__(self, user) -> None:
        self.user = user

    async def get(self, model, user_id):
        return self.user if int(user_id) == self.user.id else None


def test_password_policy_requires_complexity() -> None:
    with pytest.raises(PasswordPolicyError):
        validate_password("short", "operator")
    with pytest.raises(PasswordPolicyError):
        validate_password("lowercaseonly1!", "operator")
    with pytest.raises(PasswordPolicyError):
        validate_password("ValidPassword1!", "valid")
    validate_password("ValidPassword1!", "operator")


def test_account_lock_is_shared_across_client_ips() -> None:
    async def run() -> None:
        first_request = SimpleNamespace(
            app=app,
            client=SimpleNamespace(host="198.51.100.20"),
        )
        second_request = SimpleNamespace(
            app=app,
            client=SimpleNamespace(host="198.51.100.21"),
        )
        for _ in range(settings.LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS - 1):
            await LoginSecurityService.record_password_failure(first_request, 42)
        with pytest.raises(HTTPException) as exception:
            await LoginSecurityService.record_password_failure(first_request, 42)
        assert exception.value.status_code == 429
        with pytest.raises(HTTPException) as other_ip:
            await LoginSecurityService.ensure_account_allowed(second_request, 42)
        assert other_ip.value.status_code == 429

    anyio.run(run)


def test_refresh_token_rotates_and_reuse_revokes_family() -> None:
    async def run() -> None:
        user = SimpleNamespace(
            id=7,
            username="operator",
            status="1",
            password_changed_at=None,
            must_change_password=False,
        )
        request = SimpleNamespace(
            app=app,
            state=SimpleNamespace(mysql=FakeUserSession(user)),
        )
        Auth._refresh_cache.clear()
        access, refresh = await Auth.create_login_token_pair(
            {"user_id": user.id, "username": user.username},
            request,
        )
        assert access

        next_access, next_refresh, must_change = await Auth.refresh_login_token(
            refresh, request
        )
        assert next_access
        assert next_refresh != refresh
        assert must_change is False

        with pytest.raises(HTTPException) as reused:
            await Auth.refresh_login_token(refresh, request)
        assert reused.value.detail == "Refresh Token Reused"

        with pytest.raises(HTTPException):
            await Auth.refresh_login_token(next_refresh, request)
        Auth._refresh_cache.clear()

    anyio.run(run)


def test_totp_mfa_and_recovery_code_are_one_time() -> None:
    async def run() -> None:
        user = SimpleNamespace(
            id=7,
            username="operator",
            mfa_enabled=False,
            mfa_secret_encrypted=None,
            mfa_recovery_codes_encrypted=None,
        )
        request = SimpleNamespace(
            state=SimpleNamespace(
                user_id=user.id,
                mysql=FakeUserSession(user),
            )
        )
        setup = await MfaService.setup(request)
        await MfaService.enable(
            MfaService._totp(setup.secret, int(time.time())),
            request,
        )
        user.mfa_enabled = True
        valid_code = MfaService._totp(setup.secret, int(time.time()))
        await MfaService.verify_login(user, valid_code)
        with pytest.raises(HTTPException):
            await MfaService.verify_login(user, "000000")

        recovery_user = SimpleNamespace(**user.__dict__)
        await MfaService.verify_login(recovery_user, setup.recovery_codes[0])
        with pytest.raises(HTTPException):
            await MfaService.verify_login(recovery_user, setup.recovery_codes[0])

    anyio.run(run)
