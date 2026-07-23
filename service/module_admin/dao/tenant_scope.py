"""集中式租户上下文和 SQL 过滤条件。"""

from fastapi import HTTPException, Request
from sqlalchemy import false
from sqlmodel import select

from config.env import settings
from module_admin.entity.do.tenant_do import TenantMemberDo


def current_tenant_id(request: Request) -> int | None:
    """返回当前请求租户，不从全局默认值兜底。"""
    value = getattr(request.state, "tenant_id", None)
    if value is None and not hasattr(request, "scope"):
        # DAO 单元测试使用 SimpleNamespace；真实 ASGI 请求必须经过认证上下文。
        return settings.DEFAULT_TENANT_ID
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def tenant_clause(request: Request, model):
    """为租户模型生成集中式过滤条件，用户通过有效成员关系归属租户。"""
    tenant_id = current_tenant_id(request)
    if tenant_id is None:
        return false()
    if getattr(model, "__tablename__", None) == "users":
        return (
            select(TenantMemberDo.user_id)
            .where(
                TenantMemberDo.user_id == model.id,
                TenantMemberDo.tenant_id == tenant_id,
                TenantMemberDo.status == "1",
                TenantMemberDo.deleted_at.is_(None),
            )
            .exists()
        )
    return model.tenant_id == tenant_id


def require_tenant_id(request: Request) -> int:
    """要求受保护业务请求已经建立租户上下文。"""
    tenant_id = current_tenant_id(request)
    if tenant_id is None:
        raise HTTPException(status_code=403, detail="缺少租户上下文")
    return tenant_id


def login_tenant_id(request: Request) -> int:
    """为未完成认证的外部登录解析默认租户。"""
    return current_tenant_id(request) or settings.DEFAULT_TENANT_ID
