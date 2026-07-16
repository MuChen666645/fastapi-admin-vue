"""Code Services Model."""

import hashlib
import hmac
import json
import secrets

from fastapi import HTTPException, Request

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.entity.dto.code_dto import CaptchaImageDto
from utils.fastapi_admin import FastApiAdmin


class CodeService:
    """Code Services."""

    CAPTCHA_KEY_PREFIX = "captcha:"
    _VERIFY_SCRIPT = """
-- captcha:verify
local raw = redis.call('GET', KEYS[1])
if not raw then
    return {-1, 0}
end

local decoded, payload = pcall(cjson.decode, raw)
if not decoded then
    redis.call('DEL', KEYS[1])
    return {-1, 0}
end

if payload.ip_hash ~= ARGV[1] then
    return {-2, 0}
end

if payload.code_hash == ARGV[2] then
    redis.call('DEL', KEYS[1])
    return {1, 0}
end

local attempts = tonumber(payload.attempts or 0) + 1
if attempts >= tonumber(ARGV[3]) then
    redis.call('DEL', KEYS[1])
    return {-3, attempts}
end

payload.attempts = attempts
redis.call('SET', KEYS[1], cjson.encode(payload), 'KEEPTTL')
return {0, attempts}
"""

    @staticmethod
    def _client_ip_hash(request: Request) -> str:
        client_ip = Auth.get_client_ip(request) or "unknown"
        return hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

    @classmethod
    def _captcha_key(cls, captcha_id: str) -> str:
        return f"{cls.CAPTCHA_KEY_PREFIX}{captcha_id}"

    @staticmethod
    def _code_hash(captcha_id: str, code: str) -> str:
        message = f"captcha:{captcha_id}:{code}".encode("utf-8")
        return hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            message,
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    async def get_captcha_img_services(cls, request: Request) -> CaptchaImageDto:
        """获取验证码图片.

        Args:
            request (Request):  fastapi request.

        Returns:
            CaptchaImageDto: 验证码ID和图片.
        """
        redis = request.app.state.redis
        code = FastApiAdmin.create_random_captcha()
        captcha_id = secrets.token_urlsafe(24)
        payload = json.dumps(
            {
                "code_hash": cls._code_hash(captcha_id, code),
                "ip_hash": cls._client_ip_hash(request),
                "attempts": 0,
            },
            separators=(",", ":"),
        )
        captcha_gen = FastApiAdmin.CaptchaGenerator(code)
        image = await captcha_gen.create_captcha()
        await redis.set(
            cls._captcha_key(captcha_id),
            payload,
            ex=settings.CAPTCHA_TTL_SECONDS,
        )
        return CaptchaImageDto(captcha_id=captcha_id, image=image)

    @staticmethod
    async def get_captcha_num_services(request: Request) -> None:
        """Reject the insecure plaintext numeric captcha endpoint."""
        raise HTTPException(
            status_code=410,
            detail="数字验证码接口已停用，请使用图形验证码",
        )

    @classmethod
    async def verify_captcha_services(
        cls,
        captcha_id: str,
        code: str,
        request: Request,
    ) -> None:
        """验证验证码.

        Args:
            captcha_id (str): 验证码ID.
            code (str): 验证码.
            request (Request): fastapi request.
        """
        result = await request.app.state.redis.eval(
            cls._VERIFY_SCRIPT,
            1,
            cls._captcha_key(captcha_id),
            cls._client_ip_hash(request),
            cls._code_hash(captcha_id, code),
            settings.CAPTCHA_MAX_VERIFY_ATTEMPTS,
        )
        status = int(result[0])
        attempts = int(result[1])
        if status == 1:
            return None
        if status == -1:
            raise HTTPException(status_code=404, detail="验证码不存在或已过期")
        if status == -2:
            raise HTTPException(status_code=403, detail="验证码与当前客户端不匹配")
        if status == -3:
            raise HTTPException(
                status_code=429,
                detail="验证码校验次数过多，请重新获取验证码",
            )
        remaining_attempts = settings.CAPTCHA_MAX_VERIFY_ATTEMPTS - attempts
        raise HTTPException(
            status_code=401,
            detail=f"验证码错误，还可尝试 {remaining_attempts} 次",
        )
