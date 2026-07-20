"""Request correlation and application metrics middleware."""

import re
import secrets
import time
import uuid
from dataclasses import dataclass

from fastapi import Request
from prometheus_client import CollectorRegistry, Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"
SPAN_ID_HEADER = "X-Span-ID"
TRACEPARENT_HEADER = "traceparent"
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_TRACEPARENT_PATTERN = re.compile(
    r"^(?P<version>[0-9a-f]{2})-"
    r"(?P<trace_id>[0-9a-f]{32})-"
    r"(?P<parent_id>[0-9a-f]{16})-"
    r"(?P<flags>[0-9a-f]{2})$"
)


@dataclass(slots=True)
class ApplicationMetrics:
    """Prometheus collectors owned by one application instance."""

    registry: CollectorRegistry
    requests: Counter
    request_duration: Histogram
    exceptions: Counter

    @classmethod
    def create(cls) -> "ApplicationMetrics":
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
        )


def _request_id(value: str | None) -> str:
    """Accept safe caller IDs and replace invalid values to prevent log injection."""
    if value and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return uuid.uuid4().hex


def _trace_context(value: str | None) -> tuple[str, str, str, str]:
    """Return a trace ID, span ID, flags, and response traceparent value."""
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
    route = request.scope.get("route")
    return getattr(route, "path", "__unmatched__")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach correlation headers and record Prometheus request metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
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
        metrics: ApplicationMetrics | None = getattr(
            request.app.state, "metrics", None
        )
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
