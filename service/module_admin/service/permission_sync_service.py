"""从 FastAPI 路由同步 API 权限目录。"""

from fastapi.routing import APIRoute
from sqlmodel import select

from module_admin.entity.do.api_permission_do import ApiPermissionCatalogDo
from utils.time_utils import now_utc8_naive


class PermissionSyncService:
    """发现路由上的权限依赖并同步到数据库。"""

    @staticmethod
    def _permission_codes(route: APIRoute) -> set[str]:
        """递归读取路由依赖声明的权限编码。"""
        codes: set[str] = set()
        pending = list(getattr(route.dependant, "dependencies", []))
        while pending:
            dependency = pending.pop()
            call = getattr(dependency, "call", None)
            code = getattr(call, "permission_code", None)
            if code:
                codes.add(code)
            pending.extend(getattr(dependency, "dependencies", []))
        return codes

    @classmethod
    async def sync(cls, app, session_factory) -> int:
        """同步所有带权限依赖的 API 路由，返回目录记录数。"""
        if not callable(session_factory):
            return 0
        discovered: dict[tuple[str, str], str] = {}
        for route in app.routes:
            if not isinstance(route, APIRoute):
                continue
            codes = cls._permission_codes(route)
            for method in route.methods or set():
                for code in codes:
                    discovered[(method.upper(), route.path)] = code

        if not discovered:
            return 0
        now = now_utc8_naive()
        async with session_factory() as session:
            for (method, path), code in discovered.items():
                result = await session.execute(
                    select(ApiPermissionCatalogDo).where(
                        ApiPermissionCatalogDo.api_method == method,
                        ApiPermissionCatalogDo.api_path == path,
                    )
                )
                item = result.scalars().first()
                if item is None:
                    session.add(
                        ApiPermissionCatalogDo(
                            permission_code=code,
                            api_path=path,
                            api_method=method,
                            route_name=f"{method} {path}",
                            first_seen_at=now,
                            last_seen_at=now,
                        )
                    )
                else:
                    item.permission_code = code
                    item.status = "1"
                    item.last_seen_at = now
            await session.commit()
        return len(discovered)
