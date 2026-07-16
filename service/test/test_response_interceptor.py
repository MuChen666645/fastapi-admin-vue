import asyncio

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from httpx import ASGITransport, AsyncClient

from middleware.response_intercept import (
    ResponseInterceptor,
    SKIP_RESPONSE_WRAPPER_HEADER,
)


def run_async(coroutine):
    return asyncio.run(coroutine())


def create_test_app() -> FastAPI:
    app = FastAPI()
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
