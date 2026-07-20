import anyio

from config.env import settings
from main import create_app


class FakeRedis:
    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


def test_create_app_keeps_configuration_and_runtime_state_isolated() -> None:
    first_settings = settings.model_copy(
        update={"TITLE": "First Admin", "HOSTS": ["first.example.com"]}
    )
    second_settings = settings.model_copy(
        update={"TITLE": "Second Admin", "HOSTS": ["second.example.com"]}
    )

    first_app = create_app(first_settings)
    second_app = create_app(second_settings)

    assert first_app.title == "First Admin"
    assert second_app.title == "Second Admin"
    assert first_app.state.settings is first_settings
    assert second_app.state.settings is second_settings
    assert first_app.state is not second_app.state
    first_app.state.redis = object()
    assert second_app.state.redis is None


def test_create_app_injects_runtime_factories_and_startup_hook() -> None:
    redis = FakeRedis()
    engine = FakeEngine()
    session_factory = object()
    configured_settings = settings.model_copy(update={"TITLE": "Isolated Admin"})
    calls: list[str] = []

    async def redis_factory(app_settings):
        assert app_settings is configured_settings
        return redis

    async def mysql_factory(app_settings):
        assert app_settings is configured_settings
        return engine, session_factory

    def startup_hook() -> None:
        calls.append("started")

    application = create_app(
        configured_settings,
        redis_factory=redis_factory,
        mysql_factory=mysql_factory,
        startup_hook=startup_hook,
    )

    async def run() -> None:
        async with application.router.lifespan_context(application):
            assert application.state.redis is redis
            assert application.state.mysql_engine is engine
            assert application.state.mysql_session_factory is session_factory
            assert calls == ["started"]

        assert redis.closed
        assert engine.disposed
        assert application.state.redis is None
        assert application.state.mysql_engine is None
        assert application.state.mysql_session_factory is None

    anyio.run(run)
