import anyio
import pytest
import redis.asyncio as aioredis

from config.redis_serve import RedisServe
from test.conftest import FakeRedis, create_async_client


class ReadySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def execute(self, statement):
        return statement


class ReadySessionFactory:
    def __call__(self):
        return ReadySession()


def test_liveness_does_not_require_database() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            response = await client.get("/health/live")

        assert response.status_code == 200
        assert response.json() == {
            "code": 200,
            "message": "success",
            "data": {"status": "ok"},
        }

    anyio.run(run)


def test_readiness_checks_redis_and_mysql() -> None:
    async def run() -> None:
        from main import app

        app.state.redis = FakeRedis()
        app.state.mysql_session_factory = ReadySessionFactory()
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 200
        assert response.json()["data"] == {
            "status": "ok",
            "checks": {"redis": "ok", "mysql": "ok"},
        }

    anyio.run(run)


def test_readiness_returns_503_when_mysql_is_unavailable() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["code"] == 503
        assert body["data"] is None
        assert body["message"]["checks"]["mysql"] == "unavailable"

    anyio.run(run)


def test_redis_client_factory_is_not_awaited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeClient:
        async def ping(self):
            return True

        async def aclose(self):
            return None

    client = FakeClient()
    monkeypatch.setattr(aioredis, "from_url", lambda **kwargs: client)

    async def run() -> None:
        assert await RedisServe.get_redis_server() is client

    anyio.run(run)
