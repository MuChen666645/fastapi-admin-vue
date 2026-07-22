"""外部身份认证接口。"""

from fastapi import APIRouter, Depends, Form, Query, Request

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.external_auth_dto import ExternalAuthStartDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.external_identity_service import ExternalIdentityService


class ExternalAuthController:
    """OIDC/OAuth、LDAP 和 SSO 接口。"""

    auth = APIRouter(prefix="/auth", tags=["外部身份认证"])

    @auth.get(
        "/oidc/start",
        summary="开始 OIDC 单点登录",
        responses={200: {"model": ApiResponseDto[ExternalAuthStartDto]}},
    )
    async def oidc_start(request: Request):
        """生成 OIDC 授权地址。"""
        return await ExternalIdentityService.start_oidc(request)

    @auth.get(
        "/oidc/callback",
        summary="处理 OIDC 单点登录回调",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def oidc_callback(
        request: Request,
        code: str = Query(description="授权码"),
        state: str = Query(description="一次性状态参数"),
    ):
        """验证 OIDC 回调并签发本地令牌。"""
        return await ExternalIdentityService.callback_oidc(code, state, request)

    @auth.post(
        "/ldap/login",
        summary="LDAP 登录",
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def ldap_login(
        request: Request,
        username: str = Form(description="LDAP 用户名"),
        password: str = Form(description="LDAP 密码"),
    ):
        """通过 LDAP 认证并签发本地令牌。"""
        return await ExternalIdentityService.login_ldap(username, password, request)
