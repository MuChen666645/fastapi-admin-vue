"""基于 Redis Streams 的可靠任务队列。"""

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class TaskMessage:
    """队列消息。"""

    message_id: str
    job_id: int


class TaskQueue:
    """封装消费组、确认和崩溃消息接管。"""

    def __init__(self, redis, stream: str, group: str) -> None:
        self.redis = redis
        self.stream = stream
        self.group = group

    async def ensure_group(self) -> None:
        """创建消费组，重复创建保持幂等。"""
        try:
            await self.redis.xgroup_create(
                self.stream,
                self.group,
                id="0-0",
                mkstream=True,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def enqueue(self, job_id: int, tenant_id: int | None = None) -> str:
        """投递一个任务消息。"""
        values = {
            "job_id": str(job_id),
            "tenant_id": str(tenant_id or ""),
            "enqueued_by": uuid.uuid4().hex,
        }
        return await self.redis.xadd(
            self.stream, values, maxlen=10000, approximate=True
        )

    async def read(self, consumer: str, block_ms: int = 5000) -> TaskMessage | None:
        """先接管空闲消息，再读取新消息。"""
        claimed = await self._claim_idle(consumer)
        if claimed is not None:
            return claimed
        result = await self.redis.xreadgroup(
            self.group,
            consumer,
            {self.stream: ">"},
            count=1,
            block=block_ms,
        )
        if not result:
            return None
        _, messages = result[0]
        if not messages:
            return None
        message_id, values = messages[0]
        return self._to_message(message_id, values)

    async def ack(self, message_id: str) -> None:
        """确认任务消息。"""
        await self.redis.xack(self.stream, self.group, message_id)

    async def heartbeat(self, consumer: str, ttl_seconds: int) -> None:
        """刷新 Worker 存活标记，供运维检查消费组成员是否存活。"""
        await self.redis.set(
            f"{self.stream}:worker:{consumer}",
            "alive",
            ex=max(ttl_seconds * 3, 30),
        )

    async def clear_heartbeat(self, consumer: str) -> None:
        """停止 Worker 时移除存活标记。"""
        await self.redis.delete(f"{self.stream}:worker:{consumer}")

    async def _claim_idle(self, consumer: str) -> TaskMessage | None:
        """使用 XAUTOCLAIM 接管超时 Worker 的未确认消息。"""
        if not hasattr(self.redis, "xautoclaim"):
            return None
        result = await self.redis.xautoclaim(
            self.stream,
            self.group,
            consumer,
            min_idle_time=30000,
            start_id="0-0",
            count=1,
        )
        messages = result[1] if len(result) > 1 else []
        if not messages:
            return None
        message_id, values = messages[0]
        return self._to_message(message_id, values)

    @staticmethod
    def _to_message(message_id, values: dict) -> TaskMessage:
        """解析 Redis 字符串或字节字段。"""
        job_id = values.get("job_id", values.get(b"job_id"))
        return TaskMessage(str(message_id), int(job_id))
