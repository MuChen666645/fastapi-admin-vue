import asyncio
from test.conftest import FakeRedis, create_async_client

import anyio
import pytest
import redis.asyncio as aioredis

from config.env import settings
from config.redis_serve import RedisServe


class ReadyResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class ReadySession:
    def __init__(self, schema_version: str = settings.DATABASE_SCHEMA_VERSION):
        self.schema_version = schema_version

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None

    async def execute(self, statement):
        if "alembic_version" in str(statement):
            return ReadyResult(self.schema_version)
        return ReadyResult(1)


class ReadySessionFactory:
    def __init__(self, schema_version: str = settings.DATABASE_SCHEMA_VERSION):
        self.schema_version = schema_version

    def __call__(self):
        return ReadySession(self.schema_version)


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
            "checks": {"redis": "ok", "mysql": "ok", "schema": "ok"},
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


def test_readiness_returns_503_when_redis_is_unavailable() -> None:
    class BrokenRedis(FakeRedis):
        async def ping(self) -> bool:
            raise ConnectionError("Redis unavailable")

    async def run() -> None:
        from main import app

        app.state.redis = BrokenRedis()
        app.state.mysql_session_factory = ReadySessionFactory()
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["message"]["checks"] == {
            "redis": "unavailable",
            "mysql": "ok",
            "schema": "ok",
        }

    anyio.run(run)


def test_readiness_times_out_when_redis_hangs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class HangingRedis(FakeRedis):
        async def ping(self) -> bool:
            await asyncio.sleep(1)
            return True

    async def run() -> None:
        from config.env import settings
        from main import app

        monkeypatch.setattr(settings, "READINESS_TIMEOUT_SECONDS", 0.01)
        app.state.redis = HangingRedis()
        app.state.mysql_session_factory = ReadySessionFactory()
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        assert response.json()["message"]["checks"]["redis"] == "timeout"

    anyio.run(run)


def test_readiness_times_out_when_mysql_hangs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class HangingSession(ReadySession):
        async def execute(self, statement):
            await asyncio.sleep(1)
            return ReadyResult(1)

    class HangingSessionFactory(ReadySessionFactory):
        def __call__(self):
            return HangingSession(self.schema_version)

    async def run() -> None:
        from config.env import settings
        from main import app

        monkeypatch.setattr(settings, "READINESS_TIMEOUT_SECONDS", 0.01)
        app.state.redis = FakeRedis()
        app.state.mysql_session_factory = HangingSessionFactory()
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        assert response.json()["message"]["checks"]["mysql"] == "timeout"
        assert response.json()["message"]["checks"]["schema"] == "timeout"

    anyio.run(run)


def test_readiness_returns_503_when_schema_is_outdated() -> None:
    async def run() -> None:
        from main import app

        app.state.redis = FakeRedis()
        app.state.mysql_session_factory = ReadySessionFactory("0001_initial_schema")
        async with create_async_client() as client:
            response = await client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["message"]["checks"]["schema"] == "outdated"

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


def test_redis_client_factory_closes_client_when_ping_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenClient:
        def __init__(self) -> None:
            self.closed = False

        async def ping(self):
            raise ConnectionError("Redis unavailable")

        async def aclose(self):
            self.closed = True

    client = BrokenClient()
    monkeypatch.setattr(aioredis, "from_url", lambda **kwargs: client)

    async def run() -> None:
        with pytest.raises(RedisServe.RedisError, match="Redis connection failed"):
            await RedisServe.get_redis_server()

        assert client.closed

    anyio.run(run)
