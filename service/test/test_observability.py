import asyncio

from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
from prometheus_client import generate_latest

from middleware.observability_middleware import (
    ApplicationMetrics,
    ObservabilityMiddleware,
    TRACEPARENT_HEADER,
)
from main import create_app


def test_observability_propagates_request_and_trace_context() -> None:
    application = FastAPI()
    application.add_middleware(ObservabilityMiddleware)
    application.state.metrics = ApplicationMetrics.create()

    @application.get("/items/{item_id}")
    async def get_item(item_id: int, request: Request):
        return {
            "item_id": item_id,
            "request_id": request.state.request_id,
            "trace_id": request.state.trace_id,
        }

    async def run() -> None:
        async with AsyncClient(
            transport=ASGITransport(app=application),
            base_url="http://testserver",
        ) as client:
            response = await client.get(
                "/items/7",
                headers={
                    "X-Request-ID": "request-123",
                    TRACEPARENT_HEADER: (
                        "00-4bf92f3577b34da6a3ce929d0e0e4736-"
                        "00f067aa0ba902b7-01"
                    ),
                },
            )

        assert response.headers["X-Request-ID"] == "request-123"
        assert response.headers["X-Trace-ID"] == "4bf92f3577b34da6a3ce929d0e0e4736"
        assert len(response.headers["X-Span-ID"]) == 16
        assert response.headers[TRACEPARENT_HEADER].startswith(
            "00-4bf92f3577b34da6a3ce929d0e0e4736-"
        )
        assert response.json() == {
            "item_id": 7,
            "request_id": "request-123",
            "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
        }

    asyncio.run(run())


def test_observability_records_metrics_with_route_template() -> None:
    application = create_app()
    application.add_api_route("/health-test/{item_id}", lambda item_id: {"id": item_id})

    async def run() -> None:
        async with AsyncClient(
            transport=ASGITransport(app=application),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/health-test/7")
            metrics_response = await client.get("/metrics")

        assert response.status_code == 200
        assert metrics_response.status_code == 200
        assert metrics_response.headers["content-type"].startswith("text/plain")
        assert "http_requests_total" in metrics_response.text

    asyncio.run(run())
    output = generate_latest(application.state.metrics.registry).decode()
    assert 'http_requests_total{method="GET",path="/health-test/{item_id}"' in output
    assert "http_request_duration_seconds" in output
