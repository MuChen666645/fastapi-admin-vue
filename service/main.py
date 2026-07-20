"""Application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config.env import settings
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
    engine = None
    app.state.limiter = limiter
    app.state.redis = None
    app.state.mysql_engine = None
    app.state.mysql_session_factory = None
    try:
        app.state.redis = await RedisServe.get_redis_server()
        engine, session_factory = await MysqlServe.get_mysql_config()
        app.state.mysql_engine = engine
        app.state.mysql_session_factory = session_factory
        FastApiAdmin.start_serve()
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


app = FastAPI(
    debug=settings.DEBUG,
    title=settings.TITLE,
    summary=settings.SUMMARY,
    version=settings.VERSION,
    openapi_url=settings.OPENAPI_URL,
    responses=settings.RESPONSES,
    lifespan=lifespan,
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
ApiExceptionInterception(app)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(ResponseInterceptor)
app.add_middleware(LoggerMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.HOSTS)
add_pagination(app)
AdminAPI(app)
