"""Application entry point."""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config.env import Settings, settings
from config.mysql_serve import MysqlServe
from config.rate_limit import limiter
from config.redis_serve import RedisServe
from interceptors.http_intercept import ApiExceptionInterception
from middleware.logger_middleware import LoggerMiddleware
from middleware.response_intercept import ResponseInterceptor
from module_admin.v1 import AdminAPI
from utils.fastapi_admin import FastApiAdmin

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize runtime clients and release them on shutdown."""
    logger.info("Starting application")
    app_settings: Settings = getattr(app.state, "settings", settings)
    engine = None
    redis_factory = getattr(app.state, "redis_factory", None)
    mysql_factory = getattr(app.state, "mysql_factory", None)
    startup_hook = getattr(app.state, "startup_hook", None)
    app.state.redis = None
    app.state.mysql_engine = None
    app.state.mysql_session_factory = None
    try:
        if redis_factory is None:
            redis_factory = RedisServe.get_redis_server
            redis_args = () if app_settings is settings else (app_settings,)
            app.state.redis = await redis_factory(*redis_args)
        else:
            app.state.redis = await redis_factory(app_settings)

        if mysql_factory is None:
            mysql_factory = MysqlServe.get_mysql_config
            mysql_args = () if app_settings is settings else (app_settings,)
            engine, session_factory = await mysql_factory(*mysql_args)
        else:
            engine, session_factory = await mysql_factory(app_settings)
        app.state.mysql_engine = engine
        app.state.mysql_session_factory = session_factory
        (startup_hook or FastApiAdmin.start_serve)()
        logger.info("Application startup complete")
        yield
    finally:
        app.state.mysql_session_factory = None
        try:
            if engine is not None:
                logger.info("Closing MySQL connection")
                app.state.mysql_engine = None
                await engine.dispose()
                logger.info("MySQL connection closed")
        finally:
            await RedisServe.close_redis_server(app)


def create_app(
    app_settings: Settings | None = None,
    *,
    redis_factory: Callable[[Settings], Awaitable[Any]] | None = None,
    mysql_factory: Callable[[Settings], Awaitable[Any]] | None = None,
    startup_hook: Callable[[], None] | None = None,
    app_limiter: Limiter | None = None,
) -> FastAPI:
    """Create an isolated FastAPI application instance.

    Runtime factories and overrides are stored on the app instance so tests
    can create independent applications without mutating module globals.
    """
    configured_settings = app_settings or settings
    application = FastAPI(
        debug=configured_settings.DEBUG,
        title=configured_settings.TITLE,
        summary=configured_settings.SUMMARY,
        version=configured_settings.VERSION,
        openapi_url=configured_settings.OPENAPI_URL,
        responses=configured_settings.RESPONSES,
        lifespan=lifespan,
    )
    application.state.settings = configured_settings
    application.state.limiter = app_limiter or limiter
    application.state.redis = None
    application.state.mysql_engine = None
    application.state.mysql_session_factory = None
    if redis_factory is not None:
        application.state.redis_factory = redis_factory
    if mysql_factory is not None:
        application.state.mysql_factory = mysql_factory
    if startup_hook is not None:
        application.state.startup_hook = startup_hook

    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    ApiExceptionInterception(application)
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(ResponseInterceptor)
    application.add_middleware(LoggerMiddleware)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=configured_settings.HOSTS,
    )
    add_pagination(application)
    AdminAPI(application, configured_settings)
    return application


app = create_app()
