"""幂等请求占位、响应缓存和批量操作审计。"""

import hashlib
import json
import uuid
from datetime import timedelta

from fastapi import HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from module_admin.entity.do.operation_do import BatchOperationAuditDo, IdempotencyKeyDo
from utils.time_utils import now_utc8_naive


class IdempotencyService:
    """使用短事务实现幂等占位，并在业务事务中记录批量审计。"""

    TTL = timedelta(hours=24)

    @staticmethod
    def request_hash(request: Request, body: bytes) -> str:
        """计算包含认证范围的请求摘要，防止跨用户复用幂等键。"""
        authorization = request.headers.get("authorization", "")
        value = b"\n".join(
            [
                request.method.encode(),
                request.url.path.encode(),
                authorization.encode(),
                body,
            ]
        )
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def _scope_hash(request: Request) -> str:
        """生成不可逆的用户/租户幂等作用域。"""
        raw = "|".join(
            [
                str(getattr(request.state, "tenant_id", "")),
                str(getattr(request.state, "user_id", "")),
                request.headers.get("authorization", ""),
            ]
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    async def claim(
        cls, request: Request, key: str, request_hash: str
    ) -> IdempotencyKeyDo | None:
        """占用幂等键；已有完成结果时返回缓存记录。"""
        factory = getattr(request.app.state, "mysql_session_factory", None)
        if factory is None:
            return None
        now = now_utc8_naive()
        scope_hash = cls._scope_hash(request)
        async with factory() as session:
            result = await session.execute(
                select(IdempotencyKeyDo).where(
                    IdempotencyKeyDo.scope_hash == scope_hash,
                    IdempotencyKeyDo.idempotency_key == key,
                    IdempotencyKeyDo.method == request.method,
                    IdempotencyKeyDo.path == request.url.path,
                )
            )
            existing = result.scalars().first()
            if existing is not None and (
                existing.expires_at <= now
                or not 200 <= existing.status_code < 300
            ):
                await session.delete(existing)
                await session.flush()
                existing = None
            if existing is not None:
                if existing.request_hash != request_hash:
                    raise HTTPException(status_code=409, detail="幂等键已用于其他请求")
                if existing.status_code == 0:
                    raise HTTPException(status_code=409, detail="请求正在处理中")
                return existing
            item = IdempotencyKeyDo(
                id=str(uuid.uuid4()),
                tenant_id=getattr(request.state, "tenant_id", None),
                user_id=getattr(request.state, "user_id", None),
                scope_hash=scope_hash,
                idempotency_key=key,
                request_hash=request_hash,
                method=request.method,
                path=request.url.path,
                expires_at=now + cls.TTL,
            )
            session.add(item)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=409, detail="请求正在处理中")
            return None

    @classmethod
    async def complete(
        cls,
        request: Request,
        key: str,
        request_hash: str,
        status_code: int,
        body: bytes,
        content_type: str | None,
    ) -> None:
        """写入幂等请求最终响应。"""
        if not 200 <= status_code < 300:
            await cls.release(request, key, request_hash)
            return
        factory = getattr(request.app.state, "mysql_session_factory", None)
        if factory is None:
            return
        async with factory() as session:
            result = await session.execute(
                select(IdempotencyKeyDo).where(
                    IdempotencyKeyDo.scope_hash == cls._scope_hash(request),
                    IdempotencyKeyDo.idempotency_key == key,
                    IdempotencyKeyDo.method == request.method,
                    IdempotencyKeyDo.path == request.url.path,
                    IdempotencyKeyDo.request_hash == request_hash,
                )
            )
            item = result.scalars().first()
            if item is None:
                return
            item.status_code = status_code
            item.response_body = body.decode("utf-8")
            item.response_content_type = content_type
            await session.commit()

    @classmethod
    async def release(cls, request: Request, key: str, request_hash: str) -> None:
        """业务异常未生成可重放结果时释放占位记录，允许安全重试。"""
        factory = getattr(request.app.state, "mysql_session_factory", None)
        if factory is None:
            return
        async with factory() as session:
            result = await session.execute(
                select(IdempotencyKeyDo).where(
                    IdempotencyKeyDo.scope_hash == cls._scope_hash(request),
                    IdempotencyKeyDo.idempotency_key == key,
                    IdempotencyKeyDo.method == request.method,
                    IdempotencyKeyDo.path == request.url.path,
                    IdempotencyKeyDo.request_hash == request_hash,
                    IdempotencyKeyDo.status_code == 0,
                )
            )
            item = result.scalars().first()
            if item is not None:
                await session.delete(item)
                await session.commit()

    @staticmethod
    async def record_batch(
        request: Request,
        operation: str,
        resource_type: str,
        resource_ids: list[int | str],
        before: object | None,
        after: object | None,
        status: str = "success",
    ) -> None:
        """按业务事务记录批量操作快照。"""
        audit = BatchOperationAuditDo(
            id=str(uuid.uuid4()),
            tenant_id=getattr(request.state, "tenant_id", None),
            actor_user_id=getattr(request.state, "user_id", None),
            request_id=getattr(request.state, "request_id", None),
            operation=operation,
            resource_type=resource_type,
            resource_ids_json=json.dumps(resource_ids),
            before_json=(
                json.dumps(before, ensure_ascii=False, default=str)
                if before is not None
                else None
            ),
            after_json=(
                json.dumps(after, ensure_ascii=False, default=str)
                if after is not None
                else None
            ),
            status=status,
        )
        request_session = getattr(request.state, "mysql", None)
        if request_session is not None and hasattr(request_session, "add"):
            # 与业务写入共用事务，业务回滚时不能留下“成功”审计。
            request_session.add(audit)
            return
        factory = getattr(request.app.state, "mysql_session_factory", None)
        if factory is None:
            return
        async with factory() as session:
            session.add(audit)
            await session.commit()
