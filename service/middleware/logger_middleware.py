"""日志中间件."""

import sys
import time
import traceback

from fastapi import Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from module_admin.auth.authorization import Auth
from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import ExceptionLogDo, OperationLogDo
from utils.time_utils import now_utc8


class LoggerMiddleware(BaseHTTPMiddleware):
    """日志类."""

    _logger_configured = False

    def __init__(self, app, *args, **kwargs) -> None:
        """初始化日志中间件."""
        super().__init__(app, *args, **kwargs)
        if LoggerMiddleware._logger_configured:
            return
        logger.remove()
        logger.add(sys.stderr, colorize=True, format="{message}", level="INFO")
        logger.add(
            "{time:YYYY-MM-DD}.log",
            rotation="1 week",
            enqueue=True,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO",
        )
        logger.add(
            "{time:YYYY-MM-DD}.debug.log",
            rotation="1 week",
            enqueue=True,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="ERROR",
        )
        LoggerMiddleware._logger_configured = True

    async def dispatch(self, request: Request, call_next) -> Response:
        """重写dispatch方法.

        Args:
            request (Request): Request.
            call_next (_type_): 回调函数.

        Returns:
            Response: Response.
        """
        method = request.method
        path = request.scope["path"]
        http_type = request.scope["type"]
        current_time_china = now_utc8()
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            await self._record_exception(request, exc)
            raise
        code = response.status_code
        log_info = f"{method}——{code}——{path}——{http_type}——{current_time_china}"
        if code >= 500:
            logger.opt(colors=True).error("<red>{}</red>", log_info)
        else:
            logger.opt(colors=True).info("<green>{}</green>", log_info)
        await self._record_operation(request, code, started_at)
        return response

    @staticmethod
    async def _record_operation(request: Request, status_code: int, started_at: float) -> None:
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            return
        payload = getattr(request.state, "auth_payload", {})
        try:
            await LogDao.create_operation(
                OperationLogDo(
                    user_id=user_id,
                    username=payload.get("username"),
                    method=request.method,
                    path=request.url.path,
                    ip_address=Auth.get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    status_code=status_code,
                    duration_ms=round((time.perf_counter() - started_at) * 1000),
                ),
                request,
            )
        except Exception:
            logger.exception("Failed to persist operation log")

    @staticmethod
    async def _record_exception(request: Request, exc: Exception) -> None:
        payload = getattr(request.state, "auth_payload", {})
        try:
            await LogDao.create_exception(
                ExceptionLogDo(
                    user_id=getattr(request.state, "user_id", None),
                    username=payload.get("username"),
                    method=request.method,
                    path=request.url.path,
                    ip_address=Auth.get_client_ip(request),
                    exception_type=type(exc).__name__,
                    exception_message=str(exc)[:2000],
                    traceback="".join(traceback.format_exception(exc))[-10000:],
                ),
                request,
            )
        except Exception:
            logger.exception("Failed to persist exception log")
