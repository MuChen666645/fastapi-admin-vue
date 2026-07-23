from pathlib import Path

import anyio
import pytest
from httpx import ASGITransport, AsyncClient
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from config.mysql_serve import MysqlServe
from config.redis_serve import RedisServe
from main import STATIC_DIR, app, lifespan
from middleware.logger_middleware import LoggerMiddleware
from middleware.response_intercept import ResponseInterceptor
from utils.fastapi_admin import FastApiAdmin


class FakeRedisClient:
    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


class FailingEngine(FakeEngine):
    async def dispose(self) -> None:
        self.disposed = True
        raise RuntimeError("database close failed")


def test_application_registers_runtime_middleware_and_static_files() -> None:
    middleware_types = {middleware.cls for middleware in app.user_middleware}

    assert {
        CORSMiddleware,
        LoggerMiddleware,
        ResponseInterceptor,
        SlowAPIMiddleware,
        TrustedHostMiddleware,
    } <= middleware_types
    assert Path(STATIC_DIR).is_absolute()
    static_route = next(route for route in app.routes if route.name == "static")
    assert Path(static_route.app.directory).resolve() == STATIC_DIR


def test_lifespan_initializes_and_releases_runtime_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedisClient()
    engine = FakeEngine()
    session_factory = object()
    startup_calls: list[str] = []

    async def get_redis_server():
        return redis

    async def get_mysql_config():
        return engine, session_factory

    def start_serve() -> None:
        startup_calls.append("started")

    monkeypatch.setattr(RedisServe, "get_redis_server", staticmethod(get_redis_server))
    monkeypatch.setattr(MysqlServe, "get_mysql_config", staticmethod(get_mysql_config))
    monkeypatch.setattr(FastApiAdmin, "start_serve", staticmethod(start_serve))

    async def run() -> None:
        async with lifespan(app):
            assert app.state.redis is redis
            assert app.state.mysql_engine is engine
            assert app.state.mysql_session_factory is session_factory
            assert startup_calls == ["started"]

        assert engine.disposed
        assert redis.closed
        assert app.state.redis is None
        assert app.state.mysql_engine is None
        assert app.state.mysql_session_factory is None

    anyio.run(run)


def test_lifespan_closes_redis_when_mysql_startup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedisClient()

    async def get_redis_server():
        return redis

    async def get_mysql_config():
        raise MysqlServe.MysqlError("database unavailable")

    monkeypatch.setattr(RedisServe, "get_redis_server", staticmethod(get_redis_server))
    monkeypatch.setattr(MysqlServe, "get_mysql_config", staticmethod(get_mysql_config))

    async def run() -> None:
        with pytest.raises(MysqlServe.MysqlError, match="database unavailable"):
            async with lifespan(app):
                pass

        assert redis.closed
        assert app.state.redis is None
        assert app.state.mysql_engine is None
        assert app.state.mysql_session_factory is None

    anyio.run(run)


def test_lifespan_closes_redis_when_mysql_disposal_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis = FakeRedisClient()
    engine = FailingEngine()

    async def get_redis_server():
        return redis

    async def get_mysql_config():
        return engine, object()

    monkeypatch.setattr(RedisServe, "get_redis_server", staticmethod(get_redis_server))
    monkeypatch.setattr(MysqlServe, "get_mysql_config", staticmethod(get_mysql_config))

    async def run() -> None:
        with pytest.raises(RuntimeError, match="database close failed"):
            async with lifespan(app):
                pass

        assert engine.disposed
        assert redis.closed
        assert app.state.redis is None
        assert app.state.mysql_engine is None
        assert app.state.mysql_session_factory is None

    anyio.run(run)


def test_trusted_host_rejects_unknown_hosts() -> None:
    async def run() -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get(
                "/health/live", headers={"host": "attacker.example"}
            )

        assert response.status_code == 400

    anyio.run(run)
