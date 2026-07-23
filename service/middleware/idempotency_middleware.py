"""写请求幂等键中间件。"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from middleware.response_intercept import SKIP_RESPONSE_WRAPPER_HEADER
from module_admin.service.idempotency_service import IdempotencyService


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """缓存带 Idempotency-Key 的 JSON 写请求结果。"""

    METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next) -> Response:
        """对重复请求返回第一次执行结果。"""
        key = request.headers.get("idempotency-key", "").strip()
        if request.method not in self.METHODS or not key:
            return await call_next(request)
        if len(key) > 128:
            return Response("Idempotency-Key too long", status_code=400)

        body = await request.body()
        request_hash = IdempotencyService.request_hash(request, body)
        cached = await IdempotencyService.claim(request, key, request_hash)
        if cached is not None:
            return Response(
                content=(cached.response_body or "").encode("utf-8"),
                status_code=cached.status_code,
                media_type=cached.response_content_type,
                headers={SKIP_RESPONSE_WRAPPER_HEADER: "1"},
            )

        try:
            response = await call_next(request)
        except Exception:
            await IdempotencyService.release(request, key, request_hash)
            raise
        content_type = response.headers.get("content-type", "")
        if content_type.startswith("application/json"):
            response_body = b"".join([chunk async for chunk in response.body_iterator])
            await IdempotencyService.complete(
                request,
                key,
                request_hash,
                response.status_code,
                response_body,
                content_type,
            )
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers={
                    key: value
                    for key, value in response.headers.items()
                    if key.lower() not in {"content-length", "content-type"}
                },
                media_type=content_type,
            )
        await IdempotencyService.release(request, key, request_hash)
        return response
