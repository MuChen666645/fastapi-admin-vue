"""OpenTelemetry 追踪配置。"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_telemetry(application: FastAPI, app_settings) -> None:
    """按配置启用 FastAPI 自动埋点和 OTLP 导出。"""
    if not app_settings.OTEL_ENABLED or not app_settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        return
    headers = {}
    for item in app_settings.OTEL_EXPORTER_OTLP_HEADERS.split(","):
        if "=" in item:
            name, value = item.split("=", 1)
            headers[name.strip()] = value.strip()
    provider = TracerProvider(
        resource=Resource.create(
            {"service.name": app_settings.OTEL_SERVICE_NAME}
        )
    )
    exporter = OTLPSpanExporter(
        endpoint=app_settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        headers=headers,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(application, tracer_provider=provider)
