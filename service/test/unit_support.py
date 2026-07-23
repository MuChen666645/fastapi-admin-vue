"""单元测试专用的进程内依赖替身。"""

import json
import math
import time
from collections.abc import Set


class InMemoryRedis:
    """模拟 Redis 的最小行为，仅用于不依赖外部服务的单元测试。"""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._expires_at: dict[str, float] = {}
        self._sorted_sets: dict[str, dict[str, float]] = {}

    def _purge_expired(self, key: str) -> None:
        expires_at = self._expires_at.get(key)
        if expires_at is not None and expires_at <= time.monotonic():
            self._data.pop(key, None)
            self._expires_at.pop(key, None)

    async def get(self, key: str) -> str | None:
        self._purge_expired(key)
        return self._data.get(key)

    async def getdel(self, key: str) -> str | None:
        value = await self.get(key)
        await self.delete(key)
        return value

    async def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,
        nx: bool = False,
    ) -> bool | None:
        self._purge_expired(key)
        if nx and key in self._data:
            return None
        self._data[key] = str(value)
        if ex is None:
            self._expires_at.pop(key, None)
        else:
            self._expires_at[key] = time.monotonic() + ex
        return True

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._expires_at.pop(key, None)
        self._sorted_sets.pop(key, None)

    async def ttl(self, key: str) -> int:
        self._purge_expired(key)
        if key not in self._data:
            return -2
        expires_at = self._expires_at.get(key)
        if expires_at is None:
            return -1
        return max(math.ceil(expires_at - time.monotonic()), 0)

    async def eval(self, script: str, numkeys: int, *args) -> int | list[int]:
        if "captcha:verify" in script:
            captcha_key = args[0]
            ip_hash, submitted_code_hash, max_attempts = args[numkeys:]
            raw_payload = await self.get(captcha_key)
            if raw_payload is None:
                return [-1, 0]
            try:
                payload = json.loads(raw_payload)
            except json.JSONDecodeError:
                await self.delete(captcha_key)
                return [-1, 0]
            if payload.get("ip_hash") != ip_hash:
                return [-2, 0]
            if payload.get("code_hash") == submitted_code_hash:
                await self.delete(captcha_key)
                return [1, 0]

            attempts = int(payload.get("attempts", 0)) + 1
            if attempts >= int(max_attempts):
                await self.delete(captcha_key)
                return [-3, attempts]
            payload["attempts"] = attempts
            self._data[captcha_key] = json.dumps(payload, separators=(",", ":"))
            return [0, attempts]

        failure_key, lock_key = args[:numkeys]
        failure_window, max_failures, lock_seconds = map(
            int,
            args[numkeys:],
        )
        lock_ttl = await self.ttl(lock_key)
        if lock_ttl > 0:
            return lock_ttl

        failures = int(await self.get(failure_key) or 0) + 1
        self._data[failure_key] = str(failures)
        if failures == 1:
            self._expires_at[failure_key] = time.monotonic() + failure_window
        if failures >= max_failures:
            await self.set(lock_key, "1", ex=lock_seconds)
            await self.delete(failure_key)
            return lock_seconds
        return 0

    async def zadd(self, key: str, mapping: dict[str, float]) -> None:
        self._sorted_sets.setdefault(key, {}).update(mapping)

    async def zrem(self, key: str, *values: str) -> None:
        sorted_set = self._sorted_sets.setdefault(key, {})
        for value in values:
            sorted_set.pop(value, None)

    async def zremrangebyscore(self, key: str, minimum, maximum) -> None:
        lower = float("-inf") if minimum == "-inf" else float(minimum)
        upper = float("inf") if maximum == "+inf" else float(maximum)
        sorted_set = self._sorted_sets.setdefault(key, {})
        for member, score in list(sorted_set.items()):
            if lower <= score <= upper:
                sorted_set.pop(member)

    async def zrangebyscore(self, key: str, minimum, maximum) -> Set[str]:
        lower = float("-inf") if minimum == "-inf" else float(minimum)
        upper = float("inf") if maximum == "+inf" else float(maximum)
        return {
            member
            for member, score in self._sorted_sets.get(key, {}).items()
            if lower <= score <= upper
        }

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        self._data.clear()
        self._expires_at.clear()
        self._sorted_sets.clear()
