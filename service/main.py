"""应用入口。"""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config.env import Settings, settings
from config.mysql_serve import MysqlServe
from config.rate_limit import limiter
from config.redis_serve import RedisServe
from interceptors.http_intercept import ApiExceptionInterception
from middleware.logger_middleware import LoggerMiddleware
from middleware.observability_middleware import (
    ApplicationMetrics,
    ObservabilityMiddleware,
)
from middleware.response_intercept import ResponseInterceptor
from module_admin.v1 import AdminAPI
from module_admin.service.job_scheduler import JobScheduler, TaskHandler
from utils.fastapi_admin import FastApiAdmin

# 静态资源必须以入口文件位置为基准，避免从其他工作目录启动时失效。
STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """初始化运行时依赖，并按相反顺序释放调度器、MySQL 和 Redis。"""
    logger.info("Starting application")
    app_settings: Settings = getattr(app.state, "settings", settings)
    engine = None
    scheduler = None
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
        if app_settings.SCHEDULER_ENABLED:
            scheduler = JobScheduler(
                lambda: app.state.mysql_session_factory,
                timezone=app_settings.SCHEDULER_TIMEZONE,
            )
            for task_name, handler in getattr(app.state, "job_tasks", {}).items():
                scheduler.register_task(task_name, handler)
            app.state.scheduler = scheduler
            await scheduler.start()
        (startup_hook or FastApiAdmin.start_serve)()
        logger.info("Application startup complete")
        yield
    finally:
        if scheduler is not None:
            await scheduler.stop()
            app.state.scheduler = None
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
    job_tasks: dict[str, TaskHandler] | None = None,
) -> FastAPI:
    """创建隔离的 FastAPI 应用实例。

    运行时工厂和覆盖项保存在应用实例中，测试可以创建独立应用而不修改模块全局状态。
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
    application.state.scheduler = None
    application.state.job_tasks = job_tasks or {}
    application.state.metrics = ApplicationMetrics.create()
    if redis_factory is not None:
        application.state.redis_factory = redis_factory
    if mysql_factory is not None:
        application.state.mysql_factory = mysql_factory
    if startup_hook is not None:
        application.state.startup_hook = startup_hook

    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    async def metrics_endpoint() -> Response:
        """导出当前应用实例持有的 Prometheus 指标注册表。"""
        return Response(
            content=generate_latest(application.state.metrics.registry),
            media_type=CONTENT_TYPE_LATEST,
        )

    application.add_api_route(
        "/metrics",
        metrics_endpoint,
        methods=["GET"],
        include_in_schema=False,
        name="metrics",
    )
    ApiExceptionInterception(application)
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(ResponseInterceptor)
    application.add_middleware(LoggerMiddleware)
    application.add_middleware(ObservabilityMiddleware)
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=configured_settings.HOSTS,
    )
    add_pagination(application)
    AdminAPI(application, configured_settings)
    return application


app = create_app()
