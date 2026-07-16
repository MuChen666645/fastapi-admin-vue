"""响应拦截中间件."""

import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


SKIP_RESPONSE_WRAPPER_HEADER = "X-Skip-Response-Wrapper"
EXCLUDED_PATHS = {"/docs", "/redoc", "/openapi.json"}


def _is_json_content_type(content_type: str) -> bool:
    media_type = content_type.partition(";")[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


class ResponseInterceptor(BaseHTTPMiddleware):
    """相应类."""

    class ResponseError(Exception):
        """响应异常类."""

        pass

    async def dispatch(self, request: Request, call_next) -> JSONResponse | Response:
        """重写dispatch方法."""
        try:
            response = await call_next(request)
        except ResponseInterceptor.ResponseError:
            return JSONResponse(
                status_code=500,
                content={
                    "code": 500,
                    "data": None,
                    "message": "Internal Server Error",
                },
            )
        skip_wrapper = response.headers.get(SKIP_RESPONSE_WRAPPER_HEADER) == "1"
        if skip_wrapper:
            del response.headers[SKIP_RESPONSE_WRAPPER_HEADER]

        content_type = response.headers.get("content-type", "")
        if (
            skip_wrapper
            or request.url.path in EXCLUDED_PATHS
            or request.url.path.startswith("/static/")
            or (content_type and not _is_json_content_type(content_type))
        ):
            return response
        code = response.status_code
        response_body = b""
        cleaned_data = {}
        async for chunk in response.body_iterator:
            response_body += chunk
        if response_body:
            cleaned_data = json.loads(response_body.decode())
        if code == 200:
            data = JSONResponse(
                status_code=code,
                content={
                    "code": code,
                    "message": "success",
                    "data": cleaned_data,
                },
            )
        else:
            error_message = cleaned_data.get("detail")
            retry_after = response.headers.get("retry-after")
            data = JSONResponse(
                status_code=code,
                content={"code": code, "message": error_message, "data": None},
                headers={"Retry-After": retry_after} if retry_after else None,
            )
        return data
