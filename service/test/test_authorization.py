from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException

from module_admin.auth.authorization import Auth
from config.env import settings
from test.conftest import app


def test_revoke_login_token() -> None:
    async def run() -> None:
        request = SimpleNamespace(app=app)
        token = await Auth.create_login_token({"user_id": 1}, request)

        payload = await Auth.verify_token(request, f"Bearer {token}")
        assert payload["user_id"] == 1

        await Auth.revoke_login_token(request, f"Bearer {token}")

        with pytest.raises(HTTPException) as exception:
            await Auth.verify_token(request, f"Bearer {token}")
        assert exception.value.status_code == 401
        assert exception.value.detail == "Token Not Found"

    anyio.run(run)


def test_list_and_force_revoke_online_token() -> None:
    async def run() -> None:
        request = SimpleNamespace(app=app)
        token = await Auth.create_login_token(
            {"user_id": 7, "username": "online-user"}, request
        )

        sessions = await Auth.list_online_tokens(request)
        session = next(item for item in sessions if item["user_id"] == 7)
        assert session["username"] == "online-user"
        assert token not in str(session)

        assert await Auth.revoke_token_by_id(request, session["token_id"]) is True
        with pytest.raises(HTTPException):
            await Auth.verify_token(request, token)

    anyio.run(run)


def test_redis_revocation_invalidates_other_worker_memory_cache() -> None:
    async def run() -> None:
        request = SimpleNamespace(app=app)
        token = await Auth.create_login_token({"user_id": 9}, request)
        assert Auth._get_memory_payload(token) is not None

        await app.state.redis.delete(Auth._get_token_cache_key(token))

        with pytest.raises(HTTPException) as exception:
            await Auth.verify_token(request, token)
        assert exception.value.detail == "Token Not Found"
        assert Auth._get_memory_payload(token) is None

    anyio.run(run)


def test_client_ip_ignores_forwarded_header_from_untrusted_peer() -> None:
    original_proxies = settings.TRUSTED_PROXIES
    settings.TRUSTED_PROXIES = []
    try:
        request = SimpleNamespace(
            headers={"x-forwarded-for": "203.0.113.10"},
            client=SimpleNamespace(host="198.51.100.20"),
        )
        assert Auth.get_client_ip(request) == "198.51.100.20"
    finally:
        settings.TRUSTED_PROXIES = original_proxies


def test_client_ip_uses_rightmost_untrusted_address_from_trusted_proxy() -> None:
    original_proxies = settings.TRUSTED_PROXIES
    settings.TRUSTED_PROXIES = ["10.0.0.0/8"]
    try:
        request = SimpleNamespace(
            headers={"x-forwarded-for": "192.0.2.99, 198.51.100.30, 10.0.0.2"},
            client=SimpleNamespace(host="10.0.0.3"),
        )
        assert Auth.get_client_ip(request) == "198.51.100.30"
    finally:
        settings.TRUSTED_PROXIES = original_proxies


def test_same_user_logins_create_distinct_sessions() -> None:
    async def run() -> None:
        request = SimpleNamespace(app=app)
        first_token = await Auth.create_login_token({"user_id": 12}, request)
        second_token = await Auth.create_login_token({"user_id": 12}, request)

        assert first_token != second_token
        first_payload = Auth._decode_token(first_token)
        second_payload = Auth._decode_token(second_token)
        assert first_payload["jti"] != second_payload["jti"]
        assert "iat" in first_payload
        sessions = await Auth.list_online_tokens(request)
        assert len([item for item in sessions if item["user_id"] == 12]) == 2

    anyio.run(run)


def test_token_index_removes_expired_members() -> None:
    async def run() -> None:
        redis = app.state.redis
        await redis.zadd(Auth.TOKEN_INDEX_KEY, {"expired": 1, "active": 9999999999})

        members = await Auth._read_token_index(redis)

        assert members == {"active"}
        assert "expired" not in redis._sorted_sets[Auth.TOKEN_INDEX_KEY]

    anyio.run(run)
