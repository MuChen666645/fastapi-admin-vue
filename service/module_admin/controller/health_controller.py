"""应用健康检查探针。"""

import asyncio

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from config.env import settings


class HealthController:
    """存活探针和依赖就绪探针。"""

    health = APIRouter(prefix="/health", tags=["Health"])

    @health.get("/live", summary="Liveness probe")
    async def live() -> dict[str, str]:
        """进程可以响应请求时返回健康状态。"""
        return {"status": "ok"}

    @health.get("/ready", summary="Readiness probe")
    async def ready(request: Request) -> dict[str, object]:
        """检查业务请求依赖的外部服务和数据库版本。"""
        checks: dict[str, str] = {}

        app_settings = getattr(request.app.state, "settings", settings)
        redis = getattr(request.app.state, "redis", None)
        try:
            if redis is None:
                raise RuntimeError("Redis client is not initialized")
            await asyncio.wait_for(
                redis.ping(), timeout=app_settings.READINESS_TIMEOUT_SECONDS
            )
            checks["redis"] = "ok"
        except asyncio.TimeoutError:
            checks["redis"] = "timeout"
        except Exception:
            checks["redis"] = "unavailable"

        session_factory = getattr(request.app.state, "mysql_session_factory", None)
        try:
            if session_factory is None:
                raise RuntimeError("MySQL session factory is not initialized")
            async with asyncio.timeout(app_settings.READINESS_TIMEOUT_SECONDS):
                async with session_factory() as session:
                    await session.execute(text("SELECT 1"))
                    checks["mysql"] = "ok"
                    version_result = await session.execute(
                        text("SELECT version_num FROM alembic_version LIMIT 1")
                    )
                    version = version_result.scalar_one_or_none()
                    checks["schema"] = (
                        "ok"
                        if version == app_settings.DATABASE_SCHEMA_VERSION
                        else "outdated"
                    )
        except asyncio.TimeoutError:
            checks.setdefault("mysql", "timeout")
            checks.setdefault("schema", "timeout")
        except Exception:
            checks.setdefault("mysql", "unavailable")
            checks.setdefault("schema", "unavailable")

        if any(status != "ok" for status in checks.values()):
            raise HTTPException(
                status_code=503,
                detail={"status": "not_ready", "checks": checks},
            )
        return {"status": "ok", "checks": checks}
