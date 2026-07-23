import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from httpx import ASGITransport, AsyncClient

from interceptors.http_intercept import ApiExceptionInterception
from middleware.response_intercept import (
    SKIP_RESPONSE_WRAPPER_HEADER,
    ResponseInterceptor,
)


def run_async(coroutine):
    return asyncio.run(coroutine())


def create_test_app() -> FastAPI:
    app = FastAPI()
    ApiExceptionInterception(app)
    app.add_middleware(ResponseInterceptor)

    @app.get("/json")
    async def json_response():
        return {"value": 1}

    @app.get("/download")
    async def download_response():
        async def chunks():
            yield b"binary-"
            yield b"content"

        return StreamingResponse(
            chunks(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": 'attachment; filename="export.bin"',
                SKIP_RESPONSE_WRAPPER_HEADER: "1",
            },
        )

    @app.get("/error")
    async def error_response():
        raise RuntimeError("internal details must stay server-side")

    return app


def test_json_response_is_wrapped() -> None:
    async def run() -> None:
        app = create_test_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get("/json")

        assert response.json() == {
            "code": 200,
            "message": "success",
            "data": {"value": 1},
        }

    run_async(run)


def test_streaming_response_bypasses_wrapper() -> None:
    async def run() -> None:
        app = create_test_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get("/download")

        assert response.content == b"binary-content"
        assert response.headers["content-type"] == "application/octet-stream"
        assert response.headers["content-disposition"] == (
            'attachment; filename="export.bin"'
        )
        assert SKIP_RESPONSE_WRAPPER_HEADER not in response.headers

    run_async(run)


def test_unhandled_exception_uses_sanitized_response_contract() -> None:
    async def run() -> None:
        app = create_test_app()
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/error")

        assert response.status_code == 500
        assert response.json() == {
            "code": 500,
            "error_code": "INTERNAL_ERROR",
            "message": "Internal Server Error",
            "data": None,
        }
        assert "internal details" not in response.text

    run_async(run)
