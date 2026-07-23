"""权限模块."""

import hashlib
import ipaddress
import json
import secrets
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, Request
from sqlmodel import select

from config.env import settings
from utils.time_utils import UTC8, now_utc8


class Auth:
    """JWT 认证和接口权限校验。"""

    # Token 使用此算法签名，并按 Token 哈希值缓存。
    ALGORITHM = "HS256"
    # Redis Key 在所有应用进程之间共享。
    TOKEN_REDIS_PREFIX = "auth:token:"
    TOKEN_INDEX_KEY = "auth:token:index"
    REFRESH_REDIS_PREFIX = "auth:refresh:"
    REFRESH_REVOKED_PREFIX = "auth:refresh:revoked:"
    # Redis 不可用时使用的有界降级缓存，避免进程内存无限增长。
    MAX_MEMORY_TOKEN_CACHE_SIZE = 2048
    MAX_MEMORY_REFRESH_CACHE_SIZE = 2048
    _token_cache: OrderedDict[str, dict] = OrderedDict()
    _refresh_cache: OrderedDict[str, dict] = OrderedDict()

    # Redis 中一次性消费旧 Refresh Token 并写入新 Token，防止并发重放。
    _ROTATE_REFRESH_SCRIPT = """
local raw = redis.call('GET', KEYS[1])
if not raw then
    return {-1, ''}
end
if redis.call('EXISTS', KEYS[3]) == 1 then
    return {-2, ''}
end
local decoded, payload = pcall(cjson.decode, raw)
if not decoded then
    redis.call('DEL', KEYS[1])
    return {-1, ''}
end
if payload.used == true then
    redis.call('SET', KEYS[3], '1', 'EX', ARGV[2])
    return {-2, ''}
end
payload.used = true
redis.call('SET', KEYS[1], cjson.encode(payload), 'KEEPTTL')
redis.call('SET', KEYS[2], ARGV[1], 'EX', ARGV[2])
return {1, raw}
"""

    @staticmethod
    def create_token(data: dict) -> str:
        """为 JWT 增加签发时间、过期时间和唯一 Token ID 后签名。"""
        jwt_data = data.copy()
        issued_at = datetime.now(timezone.utc)
        exp = issued_at + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_data.update({"exp": exp, "iat": issued_at, "jti": uuid.uuid4().hex})
        return jwt.encode(jwt_data, settings.SECRET_KEY, algorithm=Auth.ALGORITHM)

    @staticmethod
    async def create_login_token(data: dict, request: Request) -> str:
        """创建 Token，并将其缓存到 Redis 或降级到进程内存。"""
        token = Auth.create_token(data)
        payload = Auth._decode_token(token)
        payload.update(
            {
                "username": data.get("username"),
                "ip_address": Auth.get_client_ip(request),
                "user_agent": getattr(request, "headers", {}).get("user-agent"),
                "login_time": now_utc8().isoformat(),
            }
        )
        await Auth._cache_token(request, token, payload)
        return token

    @staticmethod
    async def create_login_token_pair(data: dict, request: Request) -> tuple[str, str]:
        """创建短期访问令牌和可轮换刷新令牌。"""
        family_id = uuid.uuid4().hex
        token_data = {**data, "family_id": family_id}
        access_token = await Auth.create_login_token(token_data, request)
        refresh_token = await Auth.create_refresh_token(
            token_data,
            request,
            family_id=family_id,
        )
        return access_token, refresh_token

    @staticmethod
    async def create_refresh_token(
        data: dict,
        request: Request,
        family_id: str | None = None,
    ) -> str:
        """签发只保存哈希索引的刷新令牌。"""
        token = secrets.token_urlsafe(64)
        now = time.time()
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        payload = {
            "user_id": data.get("user_id"),
            "username": data.get("username"),
            "tenant_id": data.get("tenant_id"),
            "family_id": family_id or data.get("family_id") or uuid.uuid4().hex,
            "password_changed_at": data.get("password_changed_at"),
            "created_at": now,
            "expires_at": now + ttl,
            "used": False,
        }
        await Auth._store_refresh_payload(request, token, payload, ttl)
        return token

    @staticmethod
    async def verify_token(request: Request, Authorization: str | None) -> dict:
        """校验请求头、缓存记录、签名、有效期和用户 ID。"""
        if not Authorization:
            raise HTTPException(status_code=401, detail="Not Log In")

        token = Auth._parse_authorization(Authorization)
        cached_payload = await Auth._get_cached_payload(request, token)
        if cached_payload is None:
            raise HTTPException(status_code=401, detail="Token Not Found")

        try:
            payload = Auth._decode_token(token)
        except jwt.ExpiredSignatureError:
            await Auth._delete_token_cache(request, token)
            raise HTTPException(status_code=401, detail="Token Expired")
        except jwt.PyJWTError:
            await Auth._delete_token_cache(request, token)
            raise HTTPException(status_code=401, detail="Invalid Token")

        if str(cached_payload.get("user_id")) != str(payload.get("user_id")):
            await Auth._delete_token_cache(request, token)
            raise HTTPException(status_code=401, detail="Invalid Token")

        family_id = payload.get("family_id")
        if family_id and await Auth._is_refresh_family_revoked(request, family_id):
            await Auth._delete_token_cache(request, token)
            raise HTTPException(status_code=401, detail="Session Revoked")

        return payload

    @staticmethod
    async def refresh_login_token(
        refresh_token: str, request: Request
    ) -> tuple[str, str, bool]:
        """校验并轮换 Refresh Token，同时检查账号和密码版本。"""
        payload, next_refresh = await Auth._rotate_refresh_token(request, refresh_token)
        from module_admin.entity.do.user_do import UserDo

        user = await request.state.mysql.get(UserDo, int(payload["user_id"]))
        tenant_id = payload.get("tenant_id") or getattr(user, "tenant_id", None)
        if (
            user is None
            or str(user.status) != "1"
            or getattr(user, "deleted_at", None) is not None
        ):
            await Auth.revoke_refresh_family(request, payload["family_id"])
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
        if (
            tenant_id is not None
            and await Auth._get_tenant_member(request, user.id, int(tenant_id)) is None
        ):
            await Auth.revoke_refresh_family(request, payload["family_id"])
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
        current_password_version = (
            user.password_changed_at.isoformat()
            if user.password_changed_at is not None
            else None
        )
        if current_password_version != payload.get("password_changed_at"):
            await Auth.revoke_refresh_family(request, payload["family_id"])
            raise HTTPException(status_code=401, detail="Refresh Token Expired")

        data = {
            "user_id": user.id,
            "username": user.username,
            "family_id": payload["family_id"],
            "password_changed_at": current_password_version,
            "must_change_password": bool(getattr(user, "must_change_password", False)),
        }
        if tenant_id is not None:
            data["tenant_id"] = int(tenant_id)
        access_token = await Auth.create_login_token(data, request)
        return (
            access_token,
            next_refresh,
            bool(getattr(user, "must_change_password", False)),
        )

    @staticmethod
    async def revoke_refresh_family(request: Request, family_id: str) -> None:
        """撤销 Refresh Token 族，阻止同族令牌继续刷新。"""
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        redis = getattr(request.app.state, "redis", None)
        key = f"{Auth.REFRESH_REVOKED_PREFIX}{family_id}"
        if redis is not None:
            await redis.set(key, "1", ex=ttl)
            return
        Auth._store_memory_refresh_payload(
            key,
            {"payload": {"revoked": True}, "expire_at": time.time() + ttl},
        )

    @staticmethod
    async def router_auth(
        request: Request,
        Authorization: str | None = Header(default=None, description="Token"),
    ) -> dict:
        """认证请求并将已启用用户写入请求状态。"""
        return await Auth._authenticate(
            request, Authorization, allow_password_change=False
        )

    @staticmethod
    async def allow_password_change(
        request: Request,
        Authorization: str | None = Header(default=None, description="Token"),
    ) -> dict:
        """允许被强制改密账号访问自助改密接口。"""
        return await Auth._authenticate(
            request, Authorization, allow_password_change=True
        )

    @staticmethod
    async def _authenticate(
        request: Request,
        Authorization: str | None,
        allow_password_change: bool,
    ) -> dict:
        """执行 Token、用户状态和强制改密状态校验。"""
        payload = await Auth.verify_token(request, Authorization)
        user_id = Auth._get_user_id(payload)
        requested_tenant_id = payload.get("tenant_id")
        user = await Auth._get_enabled_user(request, user_id, requested_tenant_id)
        tenant_id = requested_tenant_id or getattr(user, "tenant_id", None)
        if (
            tenant_id is None
            or await Auth._get_tenant_member(request, user.id, int(tenant_id)) is None
        ):
            raise HTTPException(status_code=403, detail="用户不属于当前租户")

        if getattr(user, "must_change_password", False) and not allow_password_change:
            raise HTTPException(status_code=403, detail="请先修改密码")

        request.state.auth_payload = payload
        request.state.user_id = user.id
        request.state.tenant_id = int(tenant_id)
        return payload

    @staticmethod
    async def login_status(
        request: Request,
        Authorization: str | None = Header(default=None, description="Token"),
    ) -> dict:
        """为登录状态依赖提供统一的认证校验入口。"""
        return await Auth.router_auth(request, Authorization)

    @staticmethod
    def has_admin_role(roles: list) -> bool:
        """判断角色列表是否包含配置的保留管理员角色。"""
        admin_role_code = settings.ADMIN_ROLE_CODE.strip().casefold()
        return any(
            str(role.code).strip().casefold() == admin_role_code for role in roles
        )

    @staticmethod
    async def get_actor_roles(request: Request) -> list:
        """加载当前认证请求操作者的已启用角色。"""
        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")

        from module_admin.dao.user_dao import UserDao

        return await UserDao.get_user_roles(actor_user_id, request)

    @staticmethod
    async def revoke_login_token(request: Request, Authorization: str | None) -> None:
        """校验并撤销当前登录 Token。"""
        payload = await Auth.verify_token(request, Authorization)
        token = Auth._parse_authorization(Authorization)
        await Auth._delete_token_cache(request, token)
        if payload.get("family_id"):
            await Auth.revoke_refresh_family(request, payload["family_id"])

    @staticmethod
    def has_permission(permission_code: str):
        """创建用于按钮级权限校验的路由依赖。"""

        async def permission_dependency(
            request: Request,
            Authorization: str | None = Header(default=None, description="Token"),
        ) -> dict:
            """校验登录状态和指定按钮权限，返回认证载荷。"""
            from module_admin.dao.permission_dao import PermissionDao

            payload = await Auth.router_auth(request, Authorization)
            user_id = request.state.user_id

            if await PermissionDao.has_permission(user_id, permission_code, request):
                return payload
            raise HTTPException(status_code=403, detail="Permission Denied")

        permission_dependency.permission_code = permission_code
        return permission_dependency

    @staticmethod
    def _parse_authorization(Authorization: str) -> str:
        """从裸 Token 或 Bearer 格式的授权值中提取原始 Token。"""
        parts = Authorization.strip().split()
        if len(parts) == 1:
            return parts[0]
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        raise HTTPException(status_code=401, detail="Invalid Token")

    @staticmethod
    def _decode_token(token: str) -> dict:
        """解码并校验已签名的 JWT 载荷。"""
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[Auth.ALGORITHM])

    @staticmethod
    def _get_token_cache_key(token: str) -> str:
        """构造 Redis Key，避免在 Key 中保存原始 JWT。"""
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return f"{Auth.TOKEN_REDIS_PREFIX}{token_hash}"

    @staticmethod
    def _get_refresh_cache_key(token: str) -> str:
        """构造不包含原始 Refresh Token 的 Redis Key。"""
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return f"{Auth.REFRESH_REDIS_PREFIX}{token_hash}"

    @staticmethod
    async def _store_refresh_payload(
        request: Request, token: str, payload: dict, ttl: int
    ) -> None:
        """将刷新令牌状态写入共享 Redis 或测试用内存存储。"""
        key = Auth._get_refresh_cache_key(token)
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            await redis.set(key, json.dumps(payload), ex=ttl)
            return
        Auth._store_memory_refresh_payload(
            key,
            {
                "payload": payload,
                "expire_at": time.time() + ttl,
            },
        )

    @staticmethod
    def _store_memory_refresh_payload(key: str, value: dict) -> None:
        """写入有界刷新令牌降级缓存并清理过期条目。"""
        now = time.time()
        for cached_key, cached_value in list(Auth._refresh_cache.items()):
            if cached_value.get("expire_at", 0) <= now:
                Auth._refresh_cache.pop(cached_key, None)
        Auth._refresh_cache[key] = value
        Auth._refresh_cache.move_to_end(key)
        while len(Auth._refresh_cache) > Auth.MAX_MEMORY_REFRESH_CACHE_SIZE:
            Auth._refresh_cache.popitem(last=False)

    @staticmethod
    async def _is_refresh_family_revoked(request: Request, family_id: str) -> bool:
        """判断刷新令牌族是否已被撤销。"""
        key = f"{Auth.REFRESH_REVOKED_PREFIX}{family_id}"
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            return await redis.get(key) is not None
        cached = Auth._refresh_cache.get(key)
        if cached is None or cached.get("expire_at", 0) <= time.time():
            Auth._refresh_cache.pop(key, None)
            return False
        Auth._refresh_cache.move_to_end(key)
        return True

    @staticmethod
    async def _rotate_refresh_token(
        request: Request, refresh_token: str
    ) -> tuple[dict, str]:
        """原子消费旧令牌并写入新令牌，重放时撤销整个令牌族。"""
        old_key = Auth._get_refresh_cache_key(refresh_token)
        redis = getattr(request.app.state, "redis", None)
        if redis is None or hasattr(redis, "_data"):
            cached = Auth._refresh_cache.get(old_key)
            if redis is not None:
                raw = await redis.get(old_key)
                if raw is not None:
                    cached = {"payload": json.loads(raw), "expire_at": time.time() + 1}
            if cached is None or cached.get("expire_at", 0) <= time.time():
                Auth._refresh_cache.pop(old_key, None)
                raise HTTPException(status_code=401, detail="Invalid Refresh Token")
            payload = dict(cached["payload"])
            family_id = payload.get("family_id")
            if not family_id or await Auth._is_refresh_family_revoked(
                request, family_id
            ):
                raise HTTPException(status_code=401, detail="Invalid Refresh Token")
            if payload.get("used"):
                await Auth.revoke_refresh_family(request, family_id)
                raise HTTPException(status_code=401, detail="Refresh Token Reused")

            payload["used"] = True
            if redis is not None:
                await redis.set(old_key, json.dumps(payload), ex=60)
            else:
                cached["payload"] = payload
            next_token = secrets.token_urlsafe(64)
            next_payload = {
                **payload,
                "used": False,
                "created_at": time.time(),
                "expires_at": time.time()
                + settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            }
            await Auth._store_refresh_payload(
                request,
                next_token,
                next_payload,
                settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            )
            payload.pop("used", None)
            return payload, next_token

        raw_new_token = secrets.token_urlsafe(64)
        family_id = None
        old_raw = await redis.get(old_key)
        if old_raw is not None:
            try:
                family_id = json.loads(old_raw).get("family_id")
            except (TypeError, json.JSONDecodeError):
                family_id = None
        if not family_id:
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
        new_payload = {
            **json.loads(old_raw),
            "used": False,
            "created_at": time.time(),
            "expires_at": time.time()
            + settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        }
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        result = await redis.eval(
            Auth._ROTATE_REFRESH_SCRIPT,
            3,
            old_key,
            Auth._get_refresh_cache_key(raw_new_token),
            f"{Auth.REFRESH_REVOKED_PREFIX}{family_id}",
            json.dumps(new_payload),
            ttl,
        )
        status = int(result[0])
        if status == -2:
            raise HTTPException(status_code=401, detail="Refresh Token Reused")
        if status != 1:
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
        return json.loads(result[1]), raw_new_token

    @staticmethod
    def _get_payload_ttl(payload: dict) -> int:
        """返回 JWT 剩余有效秒数，无效过期值返回零。"""
        exp = payload.get("exp")
        if exp is None:
            return 0
        try:
            return max(int(float(exp) - time.time()), 0)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    async def _cache_token(request: Request, token: str, payload: dict) -> None:
        """优先将 Token 写入 Redis，Redis 不可用时写入有界进程缓存。"""
        ttl = Auth._get_payload_ttl(payload)
        if ttl <= 0:
            return

        cache_key = Auth._get_token_cache_key(token)
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            await redis.set(cache_key, json.dumps(payload), ex=ttl)
            await Auth._add_token_to_index(redis, cache_key, ttl)
            return

        Auth._token_cache[cache_key] = {
            "payload": payload,
            "expire_at": time.time() + ttl,
        }
        Auth._token_cache.move_to_end(cache_key)
        while len(Auth._token_cache) > Auth.MAX_MEMORY_TOKEN_CACHE_SIZE:
            Auth._token_cache.popitem(last=False)

    @staticmethod
    def _get_memory_payload(token: str) -> dict | None:
        """读取进程缓存，并延迟删除已经过期的 Token。"""
        cache_key = Auth._get_token_cache_key(token)
        cache_data = Auth._token_cache.get(cache_key)
        if cache_data is None:
            return None

        if cache_data.get("expire_at", 0) <= time.time():
            Auth._token_cache.pop(cache_key, None)
            return None
        Auth._token_cache.move_to_end(cache_key)
        return cache_data.get("payload")

    @staticmethod
    async def _get_redis_payload(request: Request, token: str) -> dict | None:
        """从 Redis 读取、校验并刷新 Token 载荷缓存。"""
        redis = getattr(request.app.state, "redis", None)
        if redis is None:
            return None

        cache_key = Auth._get_token_cache_key(token)
        cached_token = await redis.get(cache_key)
        if cached_token is None:
            await Auth._remove_token_from_index(redis, cache_key)
            return None

        try:
            payload = json.loads(cached_token)
        except json.JSONDecodeError:
            await redis.delete(cache_key)
            await Auth._remove_token_from_index(redis, cache_key)
            return None

        ttl = Auth._get_payload_ttl(payload)
        if ttl <= 0:
            await redis.delete(cache_key)
            await Auth._remove_token_from_index(redis, cache_key)
            return None

        return payload

    @staticmethod
    async def _get_cached_payload(request: Request, token: str) -> dict | None:
        """根据应用状态选择 Redis 或进程内存进行 Token 校验。"""
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            payload = await Auth._get_redis_payload(request, token)
            if payload is None:
                Auth._token_cache.pop(Auth._get_token_cache_key(token), None)
            return payload
        return Auth._get_memory_payload(token)

    @staticmethod
    async def _delete_token_cache(request: Request, token: str) -> None:
        """从所有已配置缓存中删除一个 Token。"""
        cache_key = Auth._get_token_cache_key(token)
        await Auth._delete_cache_key(request, cache_key)

    @staticmethod
    async def _delete_cache_key(request: Request, cache_key: str) -> None:
        """删除哈希 Token Key 及其有序集合索引记录。"""
        Auth._token_cache.pop(cache_key, None)
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            await redis.delete(cache_key)
            await Auth._remove_token_from_index(redis, cache_key)

    @staticmethod
    async def _add_token_to_index(redis, cache_key: str, ttl: int) -> None:
        """按过期时间建立 Token 索引，控制在线会话查询范围。"""
        now = time.time()
        await redis.zremrangebyscore(Auth.TOKEN_INDEX_KEY, "-inf", now)
        await redis.zadd(Auth.TOKEN_INDEX_KEY, {cache_key: now + ttl})

    @staticmethod
    async def _remove_token_from_index(redis, cache_key: str) -> None:
        """从 Redis 过期索引中删除一个 Token Key。"""
        await redis.zrem(Auth.TOKEN_INDEX_KEY, cache_key)

    @staticmethod
    async def _read_token_index(redis) -> set[str]:
        """清理过期索引记录并返回当前有效的 Token Key。"""
        now = time.time()
        await redis.zremrangebyscore(Auth.TOKEN_INDEX_KEY, "-inf", now)
        return set(await redis.zrangebyscore(Auth.TOKEN_INDEX_KEY, now, "+inf"))

    @staticmethod
    async def list_online_tokens(request: Request) -> list[dict]:
        """返回活跃登录会话，但不暴露原始 JWT 值。"""
        redis = getattr(request.app.state, "redis", None)
        if redis is not None:
            cache_keys = await Auth._read_token_index(redis)
        else:
            cache_keys = set(Auth._token_cache)

        sessions = []
        for cache_key in cache_keys:
            if redis is not None:
                raw_payload = await redis.get(cache_key)
                payload = None
                if raw_payload:
                    try:
                        payload = json.loads(raw_payload)
                    except (json.JSONDecodeError, TypeError):
                        payload = None
            else:
                cache_data = Auth._token_cache.get(cache_key)
                payload = cache_data.get("payload") if cache_data else None
            if payload is None or Auth._get_payload_ttl(payload) <= 0:
                await Auth._delete_cache_key(request, cache_key)
                continue
            sessions.append(
                {
                    "token_id": cache_key.removeprefix(Auth.TOKEN_REDIS_PREFIX),
                    "user_id": payload.get("user_id"),
                    "username": payload.get("username"),
                    "ip_address": payload.get("ip_address"),
                    "user_agent": payload.get("user_agent"),
                    "login_time": payload.get("login_time"),
                    "expire_time": datetime.fromtimestamp(
                        float(payload["exp"]), tz=UTC8
                    ).isoformat(),
                }
            )
        return sorted(
            sessions, key=lambda item: item.get("login_time") or "", reverse=True
        )

    @staticmethod
    async def revoke_token_by_id(request: Request, token_id: str) -> bool:
        """通过操作者数据权限校验后撤销一个会话。"""
        cache_key = f"{Auth.TOKEN_REDIS_PREFIX}{token_id}"
        sessions = await Auth.list_online_tokens(request)
        target = next(
            (session for session in sessions if session["token_id"] == token_id),
            None,
        )
        if target is None:
            return False
        state = getattr(request, "state", None)
        if state is not None and getattr(state, "mysql", None) is not None:
            from module_admin.service.data_scope_service import DataScopeService

            if not await DataScopeService.can_access_user(
                int(target["user_id"]), request
            ):
                return False
        await Auth._delete_cache_key(request, cache_key)
        return True

    @staticmethod
    async def revoke_user_tokens(request: Request, user_id: int) -> int:
        """撤销指定用户在当前操作者权限范围内的全部会话。"""
        sessions = await Auth.list_online_tokens(request)
        state = getattr(request, "state", None)
        if state is not None and getattr(state, "mysql", None) is not None:
            from module_admin.service.data_scope_service import DataScopeService

            if not await DataScopeService.can_access_user(user_id, request):
                return 0
        targets = [
            item for item in sessions if str(item.get("user_id")) == str(user_id)
        ]
        for session in targets:
            await Auth._delete_cache_key(
                request, f"{Auth.TOKEN_REDIS_PREFIX}{session['token_id']}"
            )
        return len(targets)

    @staticmethod
    async def revoke_all_user_tokens(request: Request, user_id: int) -> int:
        """在密码找回等系统流程中撤销用户全部 Access Token。"""
        sessions = await Auth.list_online_tokens(request)
        targets = [
            item for item in sessions if str(item.get("user_id")) == str(user_id)
        ]
        for session in targets:
            await Auth._delete_cache_key(
                request, f"{Auth.TOKEN_REDIS_PREFIX}{session['token_id']}"
            )
        return len(targets)

    @staticmethod
    def get_client_ip(request: Request) -> str | None:
        """解析客户端 IP，仅信任受信代理转发的请求头。"""
        client = getattr(request, "client", None)
        peer_ip = client.host if client else None
        if peer_ip is None or not Auth._is_trusted_proxy(peer_ip):
            return peer_ip

        forwarded_for = getattr(request, "headers", {}).get("x-forwarded-for")
        if not forwarded_for:
            return peer_ip

        chain = [item.strip() for item in forwarded_for.split(",") if item.strip()]
        valid_chain = []
        for candidate in chain:
            try:
                ipaddress.ip_address(candidate)
            except ValueError:
                continue
            valid_chain.append(candidate)
        for candidate in reversed(valid_chain):
            if not Auth._is_trusted_proxy(candidate):
                return candidate
        return valid_chain[0] if valid_chain else peer_ip

    @staticmethod
    def _is_trusted_proxy(address: str) -> bool:
        """检查地址是否属于已配置的代理网络。"""
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            return False
        for configured_network in settings.TRUSTED_PROXIES:
            try:
                if ip in ipaddress.ip_network(configured_network, strict=False):
                    return True
            except ValueError:
                continue
        return False

    @staticmethod
    def _get_user_id(payload: dict) -> int:
        """从已校验的 Token 载荷中解析必需的数字用户 ID。"""
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")
        try:
            return int(user_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid Token")

    @staticmethod
    async def _get_enabled_user(
        request: Request, user_id: int, tenant_id: int | None = None
    ):
        """加载目标用户，并拒绝不存在或已停用的账号。"""
        from module_admin.entity.do.user_do import UserDo

        mysql = request.state.mysql
        user = await mysql.get(UserDo, user_id)
        if user is None or getattr(user, "deleted_at", None) is not None:
            raise HTTPException(status_code=401, detail="User Not Found")
        if str(user.status) != "1":
            raise HTTPException(status_code=403, detail="User Disabled")
        if (
            tenant_id is not None
            and await Auth._get_tenant_member(request, user_id, int(tenant_id)) is None
        ):
            raise HTTPException(status_code=403, detail="用户不属于当前租户")
        return user

    @staticmethod
    async def _get_tenant_member(request: Request, user_id: int, tenant_id: int):
        """查询有效租户成员关系，所有受保护请求共用此校验。"""
        from module_admin.entity.do.tenant_do import TenantMemberDo

        result = await request.state.mysql.execute(
            select(TenantMemberDo).where(
                TenantMemberDo.user_id == user_id,
                TenantMemberDo.tenant_id == tenant_id,
                TenantMemberDo.status == "1",
                TenantMemberDo.deleted_at.is_(None),
            )
        )
        return result.scalars().first()
