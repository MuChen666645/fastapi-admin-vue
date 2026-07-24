"""写请求幂等键中间件。"""

from collections.abc import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from middleware.response_intercept import SKIP_RESPONSE_WRAPPER_HEADER
from module_admin.service.idempotency_service import IdempotencyService


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """缓存带 Idempotency-Key 的 JSON 写请求结果。"""

    METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    AUTHENTICATION_PATH_SUFFIXES = {
        "/user/login/username",
        "/user/login/phone",
        "/user/token/refresh",
        "/user/logout",
        "/user/password/forgot",
        "/user/password/reset",
        "/auth/oidc/start",
        "/auth/oidc/callback",
        "/auth/ldap/login",
    }

    @classmethod
    def _is_authentication_path(cls, request: Request) -> bool:
        path = request.url.path.rstrip("/")
        return any(path.endswith(suffix) for suffix in cls.AUTHENTICATION_PATH_SUFFIXES)

    @staticmethod
    async def _authenticate_before_claim(request: Request) -> bool:
        """在幂等记录查询前校验 Token，避免撤销会话回放历史响应。"""
        authorization = request.headers.get("authorization", "").strip()
        factory = getattr(request.app.state, "mysql_session_factory", None)
        if not authorization or factory is None:
            return False

        from module_admin.auth.authorization import Auth

        authenticator = (
            Auth.allow_password_change
            if request.url.path.rstrip("/").endswith("/user/me/password")
            else Auth.router_auth
        )
        previous_mysql = getattr(request.state, "mysql", None)
        async with factory() as session:
            request.state.mysql = session
            try:
                await authenticator(request, authorization)
            finally:
                request.state.mysql = previous_mysql
        return True

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """对重复请求返回第一次成功执行的结果。"""
        key = request.headers.get("idempotency-key", "").strip()
        if (
            request.method not in self.METHODS
            or not key
            or self._is_authentication_path(request)
        ):
            return await call_next(request)
        if len(key) > 128:
            return Response("Idempotency-Key too long", status_code=400)

        try:
            await self._authenticate_before_claim(request)
        except HTTPException:
            # 让路由依赖生成标准认证响应，同时确保不会创建或回放幂等记录。
            return await call_next(request)
        if not request.headers.get("authorization", "").strip():
            return await call_next(request)

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
        if content_type.startswith("application/json") and 200 <= response.status_code < 300:
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
