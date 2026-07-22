"""OIDC/OAuth、LDAP 和 SSO 外部身份适配服务。"""

import asyncio
import hashlib
import json
import secrets
import uuid
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, Request

from config.env import settings
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.user_do import UserDo
from module_admin.service.user_service import UserService
from utils.fastapi_admin import FastApiAdmin


class ExternalIdentityService:
    """统一处理 OIDC/OAuth、LDAP 和企业 SSO 登录。"""

    STATE_PREFIX = "auth:oidc:state:"
    STATE_TTL_SECONDS = 600

    @classmethod
    async def start_oidc(cls, request: Request) -> dict[str, str]:
        """生成一次性 OAuth/OIDC 授权地址和 state。"""
        cls._ensure_oidc_configured()
        state = secrets.token_urlsafe(32)
        payload = json.dumps({"nonce": secrets.token_urlsafe(24)})
        await request.app.state.redis.set(
            f"{cls.STATE_PREFIX}{state}",
            payload,
            ex=cls.STATE_TTL_SECONDS,
        )
        query = urlencode(
            {
                "response_type": "code",
                "client_id": settings.OIDC_CLIENT_ID,
                "redirect_uri": settings.OIDC_REDIRECT_URI,
                "scope": settings.OIDC_SCOPES,
                "state": state,
            }
        )
        separator = "&" if "?" in settings.OIDC_AUTHORIZATION_URL else "?"
        return {"authorization_url": f"{settings.OIDC_AUTHORIZATION_URL}{separator}{query}"}

    @classmethod
    async def callback_oidc(
        cls, code: str, state: str, request: Request
    ):
        """验证 state、交换 code 并登录或创建本地映射用户。"""
        cls._ensure_oidc_configured()
        state_key = f"{cls.STATE_PREFIX}{state}"
        raw_state = await request.app.state.redis.get(state_key)
        await request.app.state.redis.delete(state_key)
        if raw_state is None:
            raise HTTPException(status_code=400, detail="外部登录 state 无效或已过期")
        async with httpx.AsyncClient(timeout=10) as client:
            token_response = await client.post(
                settings.OIDC_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.OIDC_REDIRECT_URI,
                    "client_id": settings.OIDC_CLIENT_ID,
                    "client_secret": settings.OIDC_CLIENT_SECRET,
                },
            )
            token_response.raise_for_status()
            tokens = token_response.json()
            user_response = await client.get(
                settings.OIDC_USERINFO_URL,
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            user_response.raise_for_status()
            claims = user_response.json()
        return await cls._login_external_user(
            "oidc",
            str(claims.get("sub") or claims.get("id") or ""),
            claims,
            request,
        )

    @classmethod
    async def login_ldap(
        cls, username: str, password: str, request: Request
    ):
        """通过可选 LDAP 目录认证并映射本地账号。"""
        if not settings.LDAP_ENABLED:
            raise HTTPException(status_code=503, detail="LDAP 登录未启用")
        if not all((settings.LDAP_SERVER_URL, settings.LDAP_BASE_DN)):
            raise HTTPException(status_code=503, detail="LDAP 未完整配置")

        def authenticate():
            try:
                from ldap3 import ALL, Connection, Server
            except ImportError as exc:
                raise RuntimeError("LDAP 依赖未安装") from exc
            server = Server(settings.LDAP_SERVER_URL, get_info=ALL)
            bind_dn = settings.LDAP_BIND_DN or username
            connection = Connection(
                server,
                user=bind_dn,
                password=password if not settings.LDAP_BIND_DN else settings.LDAP_BIND_PASSWORD,
                auto_bind=True,
            )
            connection.search(
                settings.LDAP_BASE_DN,
                settings.LDAP_USER_FILTER.format(username=username),
                attributes=["uid", "mail", "displayName"],
            )
            entry = connection.entries[0] if connection.entries else None
            connection.unbind()
            if entry is None:
                raise ValueError("LDAP 用户不存在")
            return {
                "sub": str(entry.uid.value),
                "email": getattr(entry.mail, "value", None),
                "name": getattr(entry.displayName, "value", username),
            }

        try:
            claims = await asyncio.to_thread(authenticate)
        except Exception as exc:
            raise HTTPException(status_code=401, detail="LDAP 认证失败") from exc
        return await cls._login_external_user("ldap", claims["sub"], claims, request)

    @classmethod
    async def _login_external_user(
        cls, provider: str, subject: str, claims: dict, request: Request
    ):
        """按外部主体查找或创建本地用户并签发令牌对。"""
        if not subject:
            raise HTTPException(status_code=401, detail="外部身份缺少主体标识")
        user = await UserDao.get_user_by_external_subject(provider, subject, request)
        if user is None and claims.get("email"):
            user = await UserDao.get_user_by_identifier(str(claims["email"]), request)
        if user is None:
            username_seed = hashlib.sha256(f"{provider}:{subject}".encode()).hexdigest()[:16]
            user = UserDo(
                username=f"{provider}_{username_seed}",
                password=FastApiAdmin.password_hash(secrets.token_urlsafe(32)),
                email=claims.get("email"),
                nickname=claims.get("name") or claims.get("preferred_username"),
                auth_provider=provider,
                auth_subject=subject,
                tenant_id=settings.DEFAULT_TENANT_ID,
                must_change_password=False,
            )
            request.state.mysql.add(user)
            await request.state.mysql.flush()
        elif user.auth_subject != subject or user.auth_provider != provider:
            user.auth_provider = provider
            user.auth_subject = subject
        if str(user.status) != "1":
            raise HTTPException(status_code=403, detail="用户已停用")
        return await UserService._create_token_response(user, request)

    @staticmethod
    def _ensure_oidc_configured() -> None:
        if not settings.OIDC_ENABLED:
            raise HTTPException(status_code=503, detail="OIDC 登录未启用")
        if not all(
            (
                settings.OIDC_AUTHORIZATION_URL,
                settings.OIDC_TOKEN_URL,
                settings.OIDC_USERINFO_URL,
                settings.OIDC_CLIENT_ID,
                settings.OIDC_CLIENT_SECRET,
                settings.OIDC_REDIRECT_URI,
            )
        ):
            raise HTTPException(status_code=503, detail="OIDC 未完整配置")
