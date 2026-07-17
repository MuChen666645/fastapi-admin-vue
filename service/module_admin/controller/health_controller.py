"""Application health probes."""

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import text


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
            await redis.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unavailable"

        session_factory = getattr(request.app.state, "mysql_session_factory", None)
        try:
            if session_factory is None:
                raise RuntimeError("MySQL session factory is not initialized")
            async with session_factory() as session:
                await session.execute(text("SELECT 1"))
            checks["mysql"] = "ok"
        except Exception:
            checks["mysql"] = "unavailable"

        if any(status != "ok" for status in checks.values()):
            raise HTTPException(
                status_code=503,
                detail={"status": "not_ready", "checks": checks},
            )
        return {"status": "ok", "checks": checks}
