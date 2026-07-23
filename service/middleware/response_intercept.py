"""响应拦截中间件."""

import json

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from module_admin.error_codes import default_error_code

# 调用方可以用此请求头要求保留原始响应，处理后会移除该请求头。
SKIP_RESPONSE_WRAPPER_HEADER = "X-Skip-Response-Wrapper"
# Swagger 资源返回原始 HTML/JSON，不能套用业务响应包装。
EXCLUDED_PATHS = {"/docs", "/redoc", "/openapi.json"}


def _is_json_content_type(content_type: str) -> bool:
    """识别标准 JSON 和厂商扩展 JSON 媒体类型。"""
    media_type = content_type.partition(";")[0].strip().lower()
    return media_type == "application/json" or media_type.endswith("+json")


class ResponseInterceptor(BaseHTTPMiddleware):
    """将 JSON API 响应包装为服务统一响应结构。"""

    async def dispatch(self, request: Request, call_next) -> JSONResponse | Response:
        """原样返回非 JSON 响应，并包装 JSON 响应。"""
        response = await call_next(request)
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
            error_code = default_error_code(code)
            error_data = None
            if isinstance(error_message, dict):
                error_code = error_message.get("error_code", error_code)
                error_data = error_message.get("data")
                error_message = error_message.get("message", error_message)
            elif isinstance(error_message, list):
                error_data = {"errors": error_message}
            retry_after = response.headers.get("retry-after")
            data = JSONResponse(
                status_code=code,
                content={
                    "code": code,
                    "error_code": error_code,
                    "message": error_message,
                    "data": error_data,
                },
                headers={"Retry-After": retry_after} if retry_after else None,
            )
        for header_value in response.headers.getlist("set-cookie"):
            data.headers.append("set-cookie", header_value)
        return data
