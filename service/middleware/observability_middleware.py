"""请求关联和应用指标中间件。"""

import re
import secrets
import time
import uuid
from dataclasses import dataclass

from fastapi import Request
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# 对外返回的关联标识请求头；值会同时写入 request.state 和结构化日志。
REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"
TRACEPARENT_HEADER = "traceparent"
# 只接受安全字符，防止调用方把控制字符注入日志。
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
# W3C traceparent 的最小格式校验，拒绝全零和保留版本号。
_TRACEPARENT_PATTERN = re.compile(
    r"^(?P<version>[0-9a-f]{2})-"
    r"(?P<trace_id>[0-9a-f]{32})-"
    r"(?P<parent_id>[0-9a-f]{16})-"
    r"(?P<flags>[0-9a-f]{2})$"
)


@dataclass(slots=True)
class ApplicationMetrics:
    """由一个应用实例独立持有的 Prometheus 收集器。"""

    registry: CollectorRegistry
    requests: Counter
    request_duration: Histogram
    exceptions: Counter
    dependency_health: Gauge
    job_executions: Counter
    job_duration: Histogram
    alerts: Counter

    @classmethod
    def create(cls) -> "ApplicationMetrics":
        """为一个 FastAPI 应用创建隔离的 Prometheus 指标收集器。"""
        registry = CollectorRegistry()
        return cls(
            registry=registry,
            requests=Counter(
                "http_requests_total",
                "Total number of HTTP requests.",
                ("method", "path", "status"),
                registry=registry,
            ),
            request_duration=Histogram(
                "http_request_duration_seconds",
                "HTTP request duration in seconds.",
                ("method", "path"),
                registry=registry,
            ),
            exceptions=Counter(
                "http_request_exceptions_total",
                "Total number of uncaught HTTP request exceptions.",
                ("exception_type",),
                registry=registry,
            ),
            dependency_health=Gauge(
                "dependency_health",
                "Dependency health status (1 means healthy).",
                ("dependency",),
                registry=registry,
            ),
            job_executions=Counter(
                "scheduled_job_executions_total",
                "Scheduled job execution results.",
                ("job_id", "status"),
                registry=registry,
            ),
            job_duration=Histogram(
                "scheduled_job_duration_seconds",
                "Scheduled job execution duration.",
                ("job_id",),
                registry=registry,
            ),
            alerts=Counter(
                "alerts_sent_total",
                "Operational alerts sent.",
                ("alert_type", "status"),
                registry=registry,
            ),
        )


def _request_id(value: str | None) -> str:
    """接受安全的调用方 ID，无效值替换为随机值以防止日志注入。"""
    if value and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return uuid.uuid4().hex


def _trace_context(value: str | None) -> tuple[str, str, str, str]:
    """返回 trace ID、span ID、标志位和响应 traceparent 值。"""
    match = _TRACEPARENT_PATTERN.fullmatch((value or "").lower())
    if match and match.group("version") != "ff":
        trace_id = match.group("trace_id")
        parent_id = match.group("parent_id")
        if set(trace_id) != {"0"} and set(parent_id) != {"0"}:
            span_id = secrets.token_hex(8)
            flags = match.group("flags")
            return trace_id, span_id, flags, f"00-{trace_id}-{span_id}-{flags}"

    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return trace_id, span_id, "01", f"00-{trace_id}-{span_id}-01"


def _route_path(request: Request) -> str:
    """返回指标标签使用的路由模板。"""
    route = request.scope.get("route")
    return getattr(route, "path", "__unmatched__")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """写入请求关联请求头并记录 Prometheus 请求指标。"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """写入请求关联请求头，并记录耗时和未捕获异常。"""
        request_id = _request_id(request.headers.get(REQUEST_ID_HEADER))
        trace_id, span_id, flags, traceparent = _trace_context(
            request.headers.get(TRACEPARENT_HEADER)
        )
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        request.state.span_id = span_id
        request.state.trace_flags = flags
        request.state.traceparent = traceparent

        started_at = time.perf_counter()
        metrics: ApplicationMetrics | None = getattr(request.app.state, "metrics", None)
        try:
            response = await call_next(request)
        except Exception as exc:
            if metrics is not None:
                metrics.exceptions.labels(type(exc).__name__).inc()
            raise

        duration_seconds = time.perf_counter() - started_at
        if metrics is not None:
            path = _route_path(request)
            metrics.requests.labels(
                request.method,
                path,
                str(response.status_code),
            ).inc()
            metrics.request_duration.labels(request.method, path).observe(
                duration_seconds
            )

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[TRACE_ID_HEADER] = trace_id
        response.headers[SPAN_ID_HEADER] = span_id
        response.headers[TRACEPARENT_HEADER] = traceparent
        return response
