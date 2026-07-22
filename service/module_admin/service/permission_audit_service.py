"""权限配置版本审计服务。"""

import json

from fastapi import Request
from sqlalchemy import func
from sqlmodel import select

from module_admin.entity.do.permission_audit_do import \
    PermissionChangeVersionDo


class PermissionAuditService:
    """以独立事务记录权限配置变化前后的快照。"""

    @staticmethod
    async def record(
        request: Request,
        resource_type: str,
        resource_id: int | str,
        action: str,
        before: dict | None,
        after: dict | None,
    ) -> None:
        session_factory = getattr(request.app.state, "mysql_session_factory", None)
        if session_factory is None:
            return
        async with session_factory() as session:
            version_result = await session.execute(
                select(func.coalesce(func.max(PermissionChangeVersionDo.version), 0)).where(
                    PermissionChangeVersionDo.resource_type == resource_type,
                    PermissionChangeVersionDo.resource_id == str(resource_id),
                )
            )
            version = int(version_result.scalar_one()) + 1
            session.add(
                PermissionChangeVersionDo(
                    tenant_id=getattr(request.state, "tenant_id", None),
                    actor_user_id=getattr(request.state, "user_id", None),
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    version=version,
                    action=action,
                    before_json=json.dumps(before, ensure_ascii=False, default=str)
                    if before is not None
                    else None,
                    after_json=json.dumps(after, ensure_ascii=False, default=str)
                    if after is not None
                    else None,
                )
            )
            await session.commit()
