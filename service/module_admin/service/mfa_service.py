"""基于 TOTP 的多因素认证服务。"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import quote

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, Request

from config.env import settings
from module_admin.entity.dto.mfa_dto import MfaSetupDto


class MfaService:
    """生成、启用、校验和撤销 TOTP MFA。"""

    @staticmethod
    def _fernet() -> Fernet:
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        )
        return Fernet(key)

    @classmethod
    def _encrypt(cls, value: str) -> str:
        return cls._fernet().encrypt(value.encode("utf-8")).decode("ascii")

    @classmethod
    def _decrypt(cls, value: str | None) -> str | None:
        if not value:
            return None
        try:
            return cls._fernet().decrypt(value.encode("ascii")).decode("utf-8")
        except (InvalidToken, ValueError):
            return None

    @staticmethod
    def _secret_bytes(secret: str) -> bytes:
        padded = secret + "=" * (-len(secret) % 8)
        return base64.b32decode(padded.upper(), casefold=True)

    @classmethod
    def _totp(cls, secret: str, timestamp: int) -> str:
        counter = int(timestamp // 30).to_bytes(8, "big")
        digest = hmac.new(cls._secret_bytes(secret), counter, hashlib.sha1).digest()
        offset = digest[-1] & 0x0F
        value = int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF
        return f"{value % 1_000_000:06d}"

    @classmethod
    def verify_code(cls, secret: str, code: str, timestamp: int | None = None) -> bool:
        """在一个时间窗口内校验 TOTP。"""
        if not code or not code.isdigit() or len(code) != 6:
            return False
        now = int(time.time()) if timestamp is None else timestamp
        return any(
            hmac.compare_digest(cls._totp(secret, now + offset), code)
            for offset in (-30, 0, 30)
        )

    @staticmethod
    def _hash_recovery_code(code: str) -> str:
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            code.upper().encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    async def setup(cls, request: Request) -> MfaSetupDto:
        """生成新的 MFA 密钥和一次性恢复码。"""
        user = await cls._current_user(request)
        secret = base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")
        recovery_codes = [secrets.token_urlsafe(8).upper() for _ in range(10)]
        user.mfa_secret_encrypted = cls._encrypt(secret)
        user.mfa_recovery_codes_encrypted = cls._encrypt(
            json.dumps([cls._hash_recovery_code(code) for code in recovery_codes])
        )
        label = quote(f"{settings.MFA_ISSUER}:{user.username}")
        issuer = quote(settings.MFA_ISSUER)
        uri = (
            f"otpauth://totp/{label}?secret={secret}&issuer={issuer}"
            "&algorithm=SHA1&digits=6&period=30"
        )
        return MfaSetupDto(
            secret=secret,
            otpauth_uri=uri,
            recovery_codes=recovery_codes,
        )

    @classmethod
    async def enable(cls, code: str, request: Request) -> None:
        """使用当前 TOTP 验证码完成 MFA 启用。"""
        user = await cls._current_user(request)
        secret = cls._decrypt(user.mfa_secret_encrypted)
        if secret is None or not cls.verify_code(secret, code):
            raise HTTPException(status_code=400, detail="MFA 验证码无效")
        user.mfa_enabled = True

    @classmethod
    async def disable(cls, code: str, request: Request) -> None:
        """验证后关闭 MFA 并删除密钥和恢复码。"""
        user = await cls._current_user(request)
        await cls._verify_user_code(user, code)
        user.mfa_enabled = False
        user.mfa_secret_encrypted = None
        user.mfa_recovery_codes_encrypted = None

    @classmethod
    async def verify_login(cls, user, code: str | None) -> None:
        """在登录签发令牌前校验已启用账号的 MFA。"""
        if not getattr(user, "mfa_enabled", False):
            return
        secret = cls._decrypt(getattr(user, "mfa_secret_encrypted", None))
        if secret is None or not code:
            raise HTTPException(status_code=401, detail="需要 MFA 验证码")
        try:
            if cls.verify_code(secret, code):
                return
            recovery_codes = json.loads(
                cls._decrypt(getattr(user, "mfa_recovery_codes_encrypted", None)) or "[]"
            )
        except (json.JSONDecodeError, TypeError):
            recovery_codes = []
        code_hash = cls._hash_recovery_code(code)
        if code_hash not in recovery_codes:
            raise HTTPException(status_code=401, detail="MFA 验证码无效")
        recovery_codes.remove(code_hash)
        user.mfa_recovery_codes_encrypted = cls._encrypt(json.dumps(recovery_codes))

    @classmethod
    async def _verify_user_code(cls, user, code: str) -> None:
        secret = cls._decrypt(user.mfa_secret_encrypted)
        if secret and cls.verify_code(secret, code):
            return
        raise HTTPException(status_code=400, detail="MFA 验证码无效")

    @staticmethod
    async def _current_user(request: Request):
        from module_admin.entity.do.user_do import UserDo

        user_id = getattr(request.state, "user_id", None)
        user = await request.state.mysql.get(UserDo, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="用户不存在")
        return user
