"""登录失败计数和 IP 锁定服务。"""

import hashlib

from fastapi import HTTPException, Request

from config.env import settings
from module_admin.auth.authorization import Auth


class LoginSecurityService:
    """管理密码失败计数和临时 IP 锁定。"""

    FAILURE_KEY_PREFIX = "auth:login:failure:"
    LOCK_KEY_PREFIX = "auth:login:lock:"
    ACCOUNT_FAILURE_KEY_PREFIX = "auth:login:account:failure:"
    ACCOUNT_LOCK_KEY_PREFIX = "auth:login:account:lock:"
    # Redis Lua 保证同一客户端 IP 的失败计数和锁定创建保持原子性。
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
        """根据客户端 IP 生成不可逆的 Key 后缀。"""
        client_ip = Auth.get_client_ip(request) or "unknown"
        return hashlib.sha256(client_ip.encode("utf-8")).hexdigest()

    @staticmethod
    def _account_key_suffix(identifier: str | int) -> str:
        """根据账号标识生成不可逆的锁定 Key 后缀。"""
        normalized = str(identifier).strip().casefold()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @classmethod
    def _keys(cls, request: Request) -> tuple[str, str]:
        """构造一个客户端 IP 对应的失败计数和锁定 Key。"""
        suffix = cls._key_suffix(request)
        return (
            f"{cls.FAILURE_KEY_PREFIX}{suffix}",
            f"{cls.LOCK_KEY_PREFIX}{suffix}",
        )

    @classmethod
    def _account_keys(cls, identifier: str | int) -> tuple[str, str]:
        """构造一个账号对应的失败计数和锁定 Key。"""
        suffix = cls._account_key_suffix(identifier)
        return (
            f"{cls.ACCOUNT_FAILURE_KEY_PREFIX}{suffix}",
            f"{cls.ACCOUNT_LOCK_KEY_PREFIX}{suffix}",
        )

    @staticmethod
    def _locked_exception(remaining_seconds: int) -> HTTPException:
        """创建客户端 IP 被锁定时使用的标准限流响应。"""
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
        """拒绝来自当前仍处于锁定状态 IP 的登录请求。"""
        _, lock_key = cls._keys(request)
        remaining_seconds = int(await request.app.state.redis.ttl(lock_key))
        if remaining_seconds > 0:
            raise cls._locked_exception(remaining_seconds)

    @classmethod
    async def ensure_account_allowed(
        cls, request: Request, identifier: str | int
    ) -> None:
        """拒绝当前账号仍处于锁定状态的登录请求。"""
        _, lock_key = cls._account_keys(identifier)
        remaining_seconds = int(await request.app.state.redis.ttl(lock_key))
        if remaining_seconds > 0:
            raise HTTPException(
                status_code=429,
                detail=(
                    "登录失败次数过多，当前账号已锁定，"
                    f"请在 {remaining_seconds} 秒后重试"
                ),
                headers={"Retry-After": str(remaining_seconds)},
            )

    @classmethod
    async def record_password_failure(
        cls, request: Request, identifier: str | int | None = None
    ) -> None:
        """原子记录密码失败次数，达到阈值时锁定 IP 或账号。"""
        if identifier is None:
            failure_key, lock_key = cls._keys(request)
            max_failures = settings.LOGIN_MAX_FAILED_ATTEMPTS
            lock_seconds = settings.LOGIN_IP_LOCK_SECONDS
        else:
            failure_key, lock_key = cls._account_keys(identifier)
            max_failures = settings.LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS
            lock_seconds = settings.LOGIN_ACCOUNT_LOCK_SECONDS
        remaining_seconds = int(
            await request.app.state.redis.eval(
                cls._REGISTER_FAILURE_SCRIPT,
                2,
                failure_key,
                lock_key,
                lock_seconds,
                max_failures,
                lock_seconds,
            )
        )
        if remaining_seconds > 0:
            raise cls._locked_exception(remaining_seconds)

    @classmethod
    async def clear_password_failures(
        cls, request: Request, identifier: str | int | None = None
    ) -> None:
        """密码正确后清除对应的失败计数。"""
        if identifier is None:
            failure_key, _ = cls._keys(request)
        else:
            failure_key, _ = cls._account_keys(identifier)
        await request.app.state.redis.delete(failure_key)
