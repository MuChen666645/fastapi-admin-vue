"""外部身份认证接口。"""

from fastapi import APIRouter, Form, Query, Request

from config.env import settings
from config.rate_limit import limiter
from module_admin.entity.dto.external_auth_dto import ExternalAuthStartDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.external_identity_service import \
    ExternalIdentityService


class ExternalAuthController:
    """OIDC/OAuth、LDAP 和 SSO 接口。"""

    auth = APIRouter(prefix="/auth", tags=["外部身份认证"])

    @auth.get(
        "/oidc/start",
        summary="开始 OIDC 单点登录",
        responses={200: {"model": ApiResponseDto[ExternalAuthStartDto]}},
    )
    @limiter.limit(settings.RATE_LIMIT_EXTERNAL_AUTH)
    async def oidc_start(request: Request):
        """生成 OIDC 授权地址。"""
        return await ExternalIdentityService.start_oidc(request)

    @auth.get(
        "/oidc/callback",
        summary="处理 OIDC 单点登录回调",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    @limiter.limit(settings.RATE_LIMIT_EXTERNAL_AUTH)
    async def oidc_callback(
        request: Request,
        code: str = Query(description="授权码"),
        state: str = Query(description="一次性状态参数"),
        mfa_code: str | None = Query(default=None, description="MFA 验证码或恢复码"),
    ):
        """验证 OIDC 回调并签发本地令牌。"""
        return await ExternalIdentityService.callback_oidc(
            code, state, request, mfa_code
        )

    @auth.post(
        "/ldap/login",
        summary="LDAP 登录",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    @limiter.limit(settings.RATE_LIMIT_EXTERNAL_AUTH)
    async def ldap_login(
        request: Request,
        username: str = Form(description="LDAP 用户名"),
        password: str = Form(description="LDAP 密码"),
        mfa_code: str | None = Form(default=None, description="MFA 验证码或恢复码"),
    ):
        """通过 LDAP 认证并签发本地令牌。"""
        return await ExternalIdentityService.login_ldap(
            username, password, request, mfa_code
        )
