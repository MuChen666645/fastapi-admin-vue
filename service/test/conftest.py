import inspect
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from test.unit_support import InMemoryRedis

import pytest
from httpx import ASGITransport, AsyncClient
from limits.storage import MemoryStorage

test_environment_defaults = {
    "APP_ENV": "development",
    "DEBUG": "true",
    "MYSQL_HOST": "127.0.0.1",
    "MYSQL_POST": "3306",
    "MYSQL_USERNAME": "test",
    "MYSQL_PASSWORD": "test",
    "MYSQL_DATABASES": "test",
    "TIMEZONE": "Asia/Shanghai",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_POST": "6379",
    "REDIS_PASSWORD": "",
    "REDIS_USERNAME": "",
    "REDIS_DB": "0",
    "SECRET_KEY": "test-only-secret-key-that-is-long-enough",
    "HOSTS": '["testserver", "localhost", "127.0.0.1"]',
    "ACCESS_KEY_ID": "test",
    "ACCESSKEY_SECRET": "test",
}
if os.getenv("RUN_INTEGRATION_TESTS") == "1":
    # Real tests read service credentials from the selected environment file or
    # from CI-provided variables instead of receiving unit-test placeholders.
    test_environment_defaults = {
        "APP_ENV": "development",
        "DEBUG": "false",
        "MYSQL_HOST": "127.0.0.1",
        "REDIS_HOST": "127.0.0.1",
    }

for key, value in test_environment_defaults.items():
    os.environ.setdefault(key, value)

# Real tests create temporary rows, so never inherit a staging or production
# profile from the shell that launched pytest.
if os.getenv("APP_ENV") != "development":
    os.environ["APP_ENV"] = "development"
if os.getenv("RUN_INTEGRATION_TESTS") == "1":
    os.environ["DEBUG"] = "false"
elif os.getenv("DEBUG", "").strip().lower() not in {
    "true",
    "false",
    "1",
    "0",
    "yes",
    "no",
    "on",
    "off",
}:
    os.environ["DEBUG"] = "true"

from config.mysql_serve import bind_request_mysql_session
from main import app, limiter
from middleware.logger_middleware import LoggerMiddleware

LoggerMiddleware._logger_configured = True


@asynccontextmanager
async def create_async_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def allow_auth_dependency() -> dict[str, int]:
    return {"user_id": 1}


async def skip_mysql_session() -> AsyncIterator[None]:
    yield


@pytest.fixture(autouse=True)
def isolate_app_dependencies(request: pytest.FixtureRequest) -> AsyncIterator[None]:
    if request.node.get_closest_marker("integration") is not None:
        # Integration tests own the application lifespan and must not inherit
        # the in-memory Redis or dependency overrides used by unit tests.
        app.state.redis = None
        app.state.mysql_session_factory = None
        app.dependency_overrides.clear()
        yield
        app.dependency_overrides.clear()
        return

    # Unit tests use isolated storage; production is configured with Redis in
    # config.rate_limit and is verified separately by the rate-limit tests.
    limiter._storage = MemoryStorage()
    limiter._limiter = type(limiter._limiter)(limiter._storage)
    limiter._storage_dead = False
    limiter.enabled = False
    app.state.limiter = limiter
    app.state.redis = InMemoryRedis()
    app.state.mysql_session_factory = None
    app.dependency_overrides.clear()
    app.dependency_overrides[bind_request_mysql_session] = skip_mysql_session

    for route in app.routes:
        dependant = getattr(route, "dependant", None)
        if dependant is None:
            continue
        for dependency in dependant.dependencies:
            if dependency.call is bind_request_mysql_session:
                continue
            if inspect.isclass(dependency.call):
                continue
            app.dependency_overrides[dependency.call] = allow_auth_dependency

    yield

    app.dependency_overrides.clear()
