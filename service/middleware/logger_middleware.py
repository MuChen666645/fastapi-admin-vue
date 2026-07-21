"""结构化访问日志和数据库审计日志中间件。"""

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
    """写入结构化 HTTP 日志和已认证操作审计记录。"""

    _logger_configured = False

    def __init__(self, app, *args, **kwargs) -> None:
        """在当前进程中只配置一次结构化日志输出。"""
        super().__init__(app, *args, **kwargs)
        if LoggerMiddleware._logger_configured:
            return
        logger.remove()
        logger.add(sys.stderr, serialize=True, level="INFO")
        logger.add(
            "{time:YYYY-MM-DD}.log",
            rotation="1 week",
            enqueue=True,
            serialize=True,
            level="INFO",
        )
        logger.add(
            "{time:YYYY-MM-DD}.debug.log",
            rotation="1 week",
            enqueue=True,
            serialize=True,
            level="ERROR",
        )
        LoggerMiddleware._logger_configured = True

    async def dispatch(self, request: Request, call_next) -> Response:
        """记录一次请求，并为已认证用户持久化审计记录。"""
        started_at = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            await self._record_exception(request, exc)
            raise

        status_code = response.status_code
        logger.bind(
            request_id=getattr(request.state, "request_id", None),
            trace_id=getattr(request.state, "trace_id", None),
            span_id=getattr(request.state, "span_id", None),
            method=request.method,
            path=request.scope["path"],
            http_type=request.scope["type"],
            request_time=now_utc8().isoformat(),
        ).log(
            "ERROR" if status_code >= 500 else "INFO",
            "http_request",
            status_code=status_code,
            duration_ms=round((time.perf_counter() - started_at) * 1000),
        )
        await self._record_operation(request, status_code, started_at)
        return response

    @staticmethod
    async def _record_operation(
        request: Request,
        status_code: int,
        started_at: float,
    ) -> None:
        """将已认证请求持久化为操作审计记录。"""
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
        """将异常写入结构化日志和异常审计表。"""
        payload = getattr(request.state, "auth_payload", {})
        logger.bind(
            request_id=getattr(request.state, "request_id", None),
            trace_id=getattr(request.state, "trace_id", None),
            span_id=getattr(request.state, "span_id", None),
            method=request.method,
            path=request.url.path,
            exception_type=type(exc).__name__,
        ).exception("http_request_failed")
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
