"""应用入口。"""

import asyncio
import hmac
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from loguru import logger
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_503_SERVICE_UNAVAILABLE

from config.env import Settings, settings
from config.mysql_serve import MysqlServe
from config.rate_limit import limiter
from config.redis_serve import RedisServe
from interceptors.http_intercept import ApiExceptionInterception
from middleware.idempotency_middleware import IdempotencyMiddleware
from middleware.logger_middleware import LoggerMiddleware
from middleware.observability_middleware import (
    ApplicationMetrics,
    ObservabilityMiddleware,
)
from middleware.response_intercept import ResponseInterceptor
from middleware.telemetry import configure_telemetry
from module_admin.service.export_service import ExportService
from module_admin.service.file_service import FileService
from module_admin.service.job_scheduler import JobScheduler, TaskHandler
from module_admin.service.notification_service import NotificationService
from module_admin.service.permission_sync_service import PermissionSyncService
from module_admin.service.retention_service import RetentionService
from module_admin.v1 import AdminAPI
from utils.fastapi_admin import FastApiAdmin

# 静态资源必须以入口文件位置为基准，避免从其他工作目录启动时失效。
STATIC_DIR = Path(__file__).resolve().parent / "static"


async def _file_chunk_cleanup_loop(session_factory, app_settings: Settings) -> None:
    """定期清理中断的分片上传，避免临时文件长期占用磁盘。"""
    interval = min(max(app_settings.FILE_CHUNK_TTL_SECONDS // 2, 60), 3600)
    while True:
        try:
            await FileService.cleanup_expired_chunks(session_factory, app_settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("清理过期分片上传失败")
        await asyncio.sleep(interval)


async def _notification_delivery_loop(session_factory, app_settings: Settings) -> None:
    """定期发送到期通知，并由通知服务负责退避重试。"""
    interval = min(max(app_settings.NOTIFICATION_RETRY_BASE_SECONDS, 5), 60)
    while True:
        try:
            await NotificationService.deliver_pending(session_factory, app_settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("通知投递循环执行失败")
        await asyncio.sleep(interval)


async def _retention_cleanup_loop(session_factory, app_settings: Settings) -> None:
    """定期清理幂等键、审计、日志和已完成通知投递记录。"""
    interval = max(app_settings.RETENTION_CLEANUP_INTERVAL_SECONDS, 60)
    while True:
        try:
            await RetentionService.cleanup(session_factory, app_settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("数据库保留期清理失败")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """初始化运行时依赖，并按相反顺序释放调度器、MySQL 和 Redis。"""
    logger.info("Starting application")
    app_settings: Settings = getattr(app.state, "settings", settings)
    engine = None
    scheduler = None
    chunk_cleanup_task = None
    notification_delivery_task = None
    retention_cleanup_task = None
    export_worker_task = None
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
        await PermissionSyncService.sync(app, session_factory)
        chunk_cleanup_task = asyncio.create_task(
            _file_chunk_cleanup_loop(session_factory, app_settings)
        )
        notification_delivery_task = asyncio.create_task(
            _notification_delivery_loop(session_factory, app_settings)
        )
        retention_cleanup_task = asyncio.create_task(
            _retention_cleanup_loop(session_factory, app_settings)
        )
        export_worker_task = asyncio.create_task(
            ExportService.worker_loop(session_factory, app_settings)
        )
        if app_settings.SCHEDULER_ENABLED:
            scheduler = JobScheduler(
                lambda: app.state.mysql_session_factory,
                timezone=app_settings.SCHEDULER_TIMEZONE,
                redis=app.state.redis,
                default_timeout=app_settings.SCHEDULER_DEFAULT_TIMEOUT_SECONDS,
                lock_ttl=app_settings.SCHEDULER_LOCK_TTL_SECONDS,
                default_max_retries=app_settings.SCHEDULER_DEFAULT_MAX_RETRIES,
                worker_mode=app_settings.SCHEDULER_WORKER_MODE,
                queue_stream=app_settings.TASK_QUEUE_STREAM,
                queue_group=app_settings.TASK_QUEUE_GROUP,
                lock_renew_seconds=app_settings.TASK_LOCK_RENEW_SECONDS,
                metrics=app.state.metrics,
                alert_webhook_url=app_settings.ALERT_WEBHOOK_URL,
            )
            for task_name, handler in getattr(app.state, "job_tasks", {}).items():
                scheduler.register_task(task_name, handler)
            app.state.scheduler = scheduler
            await scheduler.start()
        (startup_hook or FastApiAdmin.start_serve)()
        logger.info("Application startup complete")
        yield
    finally:
        if chunk_cleanup_task is not None:
            chunk_cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await chunk_cleanup_task
        if notification_delivery_task is not None:
            notification_delivery_task.cancel()
            with suppress(asyncio.CancelledError):
                await notification_delivery_task
        if retention_cleanup_task is not None:
            retention_cleanup_task.cancel()
            with suppress(asyncio.CancelledError):
                await retention_cleanup_task
        if export_worker_task is not None:
            export_worker_task.cancel()
            with suppress(asyncio.CancelledError):
                await export_worker_task
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
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
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
    configure_telemetry(application, configured_settings)
    if redis_factory is not None:
        application.state.redis_factory = redis_factory
    if mysql_factory is not None:
        application.state.mysql_factory = mysql_factory
    if startup_hook is not None:
        application.state.startup_hook = startup_hook

    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    def operations_access(expected: str):
        """生成生产环境运维资源的访问依赖。"""

        async def check(request: Request) -> None:
            if configured_settings.DEBUG:
                return
            if not expected:
                raise HTTPException(
                    status_code=HTTP_503_SERVICE_UNAVAILABLE,
                    detail="运维访问令牌未配置",
                )
            provided = request.headers.get("x-operations-token", "")
            authorization = request.headers.get("authorization", "")
            if not provided and authorization.lower().startswith("bearer "):
                provided = authorization[7:].strip()
            if not hmac.compare_digest(provided, expected):
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="未授权")

        return check

    async def metrics_endpoint(request: Request) -> Response:
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
        dependencies=[
            Depends(operations_access(configured_settings.METRICS_AUTH_TOKEN))
        ],
    )

    openapi_path = configured_settings.OPENAPI_URL

    async def openapi_endpoint(request: Request) -> JSONResponse:
        """返回受保护的 OpenAPI 文档。"""
        return JSONResponse(application.openapi())

    async def swagger_endpoint(request: Request) -> Response:
        """返回受保护的 Swagger UI。"""
        return get_swagger_ui_html(
            openapi_url=openapi_path,
            title=f"{configured_settings.TITLE} - Swagger UI",
        )

    async def redoc_endpoint(request: Request) -> Response:
        """返回受保护的 ReDoc 页面。"""
        return get_redoc_html(
            openapi_url=openapi_path,
            title=f"{configured_settings.TITLE} - ReDoc",
        )

    application.add_api_route(
        openapi_path,
        openapi_endpoint,
        methods=["GET"],
        include_in_schema=False,
        name="openapi",
        dependencies=[Depends(operations_access(configured_settings.DOCS_AUTH_TOKEN))],
    )
    application.add_api_route(
        "/docs",
        swagger_endpoint,
        methods=["GET"],
        include_in_schema=False,
        name="swagger_ui",
        dependencies=[Depends(operations_access(configured_settings.DOCS_AUTH_TOKEN))],
    )
    application.add_api_route(
        "/redoc",
        redoc_endpoint,
        methods=["GET"],
        include_in_schema=False,
        name="redoc",
        dependencies=[Depends(operations_access(configured_settings.DOCS_AUTH_TOKEN))],
    )
    ApiExceptionInterception(application)
    application.add_middleware(SlowAPIMiddleware)
    application.add_middleware(ResponseInterceptor)
    application.add_middleware(IdempotencyMiddleware)
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
