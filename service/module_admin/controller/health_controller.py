"""Application health probes."""

import asyncio

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text

from config.env import settings


class HealthController:
    """Liveness and dependency readiness probes."""

    health = APIRouter(prefix="/health", tags=["Health"])

    @health.get("/live", summary="Liveness probe")
    async def live() -> dict[str, str]:
        """Return healthy while the process can serve requests."""
        return {"status": "ok"}

    @health.get("/ready", summary="Readiness probe")
    async def ready(request: Request) -> dict[str, object]:
        """Verify dependencies needed by business requests."""
        checks: dict[str, str] = {}

        redis = getattr(request.app.state, "redis", None)
        try:
            if redis is None:
                raise RuntimeError("Redis client is not initialized")
            await asyncio.wait_for(
                redis.ping(), timeout=settings.READINESS_TIMEOUT_SECONDS
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
            async with asyncio.timeout(settings.READINESS_TIMEOUT_SECONDS):
                async with session_factory() as session:
                    await session.execute(text("SELECT 1"))
                    checks["mysql"] = "ok"
                    version_result = await session.execute(
                        text("SELECT version_num FROM alembic_version LIMIT 1")
                    )
                    version = version_result.scalar_one_or_none()
                    checks["schema"] = (
                        "ok"
                        if version == settings.DATABASE_SCHEMA_VERSION
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
