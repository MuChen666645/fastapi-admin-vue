"""Login failure tracking and IP lockout services."""

import hashlib

from fastapi import HTTPException, Request

from config.env import settings
from module_admin.auth.authorization import Auth


class LoginSecurityService:
    """Manage password failure counters and temporary IP locks."""

    FAILURE_KEY_PREFIX = "auth:login:failure:"
    LOCK_KEY_PREFIX = "auth:login:lock:"
    _REGISTER_FAILURE_SCRIPT = """
local lock_ttl = redis.call('TTL', KEYS[2])
if lock_ttl > 0 then
    return lock_ttl
end

local failures = redis.call('INCR', KEYS[1])
if failures == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

if failures >= tonumber(ARGV[2]) then
    redis.call('SET', KEYS[2], '1', 'EX', ARGV[3])
    redis.call('DEL', KEYS[1])
    return tonumber(ARGV[3])
end

return 0
"""

    @staticmethod
    def _key_suffix(request: Request) -> str:
        client_ip = Auth.get_client_ip(request) or "unknown"
        return hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

    @classmethod
    def _keys(cls, request: Request) -> tuple[str, str]:
        suffix = cls._key_suffix(request)
        return (
            f"{cls.FAILURE_KEY_PREFIX}{suffix}",
            f"{cls.LOCK_KEY_PREFIX}{suffix}",
        )

    @staticmethod
    def _locked_exception(remaining_seconds: int) -> HTTPException:
        return HTTPException(
            status_code=429,
            detail=(
                "登录失败次数过多，当前 IP 已锁定，"
                f"请在 {remaining_seconds} 秒后重试"
            ),
            headers={"Retry-After": str(remaining_seconds)},
        )

    @classmethod
    async def ensure_ip_allowed(cls, request: Request) -> None:
        """Reject login attempts from an IP with an active lock."""
        _, lock_key = cls._keys(request)
        remaining_seconds = int(await request.app.state.redis.ttl(lock_key))
        if remaining_seconds > 0:
            raise cls._locked_exception(remaining_seconds)

    @classmethod
    async def record_password_failure(cls, request: Request) -> None:
        """Atomically record a failure and lock the IP at the threshold."""
        failure_key, lock_key = cls._keys(request)
        remaining_seconds = int(
            await request.app.state.redis.eval(
                cls._REGISTER_FAILURE_SCRIPT,
                2,
                failure_key,
                lock_key,
                settings.LOGIN_IP_LOCK_SECONDS,
                settings.LOGIN_MAX_FAILED_ATTEMPTS,
                settings.LOGIN_IP_LOCK_SECONDS,
            )
        )
        if remaining_seconds > 0:
            raise cls._locked_exception(remaining_seconds)

    @classmethod
    async def clear_password_failures(cls, request: Request) -> None:
        """Clear the rolling failure counter after a correct password."""
        failure_key, _ = cls._keys(request)
        await request.app.state.redis.delete(failure_key)
