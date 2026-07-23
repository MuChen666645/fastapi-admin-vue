"""租户管理、成员关系和租户切换业务服务。"""

from fastapi import HTTPException, Request
from sqlmodel import select

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.tenant_dao import TenantDao
from module_admin.entity.do.tenant_do import TenantDo
from module_admin.entity.do.user_do import UserDo


class TenantService:
    """执行租户生命周期和成员关系的业务校验。"""

    @staticmethod
    async def list_current_user(request: Request):
        """查询当前用户可切换的租户。"""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="未登录")
        return await TenantDao.list_for_user(int(user_id), request)

    @staticmethod
    async def list_all(request: Request):
        """查询平台租户列表。"""
        return await TenantDao.list_all(request)

    @staticmethod
    async def switch(tenant_id: int, request: Request):
        """校验成员关系并签发目标租户的新令牌族。"""
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="未登录")
        tenant = await TenantDao.get(tenant_id, request)
        member = await TenantDao.get_member(int(user_id), tenant_id, request)
        if tenant is None or tenant.status != "1" or member is None:
            raise HTTPException(status_code=403, detail="无权切换到该租户")
        user = await request.state.mysql.get(UserDo, int(user_id))
        if (
            user is None
            or str(user.status) != "1"
            or getattr(user, "deleted_at", None) is not None
        ):
            raise HTTPException(status_code=401, detail="用户不存在或已停用")
        password_changed_at = (
            user.password_changed_at.isoformat()
            if user.password_changed_at is not None
            else None
        )
        access_token, refresh_token = await Auth.create_login_token_pair(
            {
                "user_id": user.id,
                "username": user.username,
                "tenant_id": tenant_id,
                "password_changed_at": password_changed_at,
                "must_change_password": bool(user.must_change_password),
            },
            request,
        )
        old_family = getattr(request.state, "auth_payload", {}).get("family_id")
        if old_family:
            await Auth.revoke_refresh_family(request, old_family)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "tenant_id": tenant_id,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    async def create(data, request: Request) -> TenantDo:
        """创建租户并将当前用户设为默认成员。"""
        result = await request.state.mysql.execute(
            select(TenantDo).where(
                TenantDo.code == data.code,
                TenantDo.deleted_at.is_(None),
            )
        )
        if result.scalars().first() is not None:
            raise HTTPException(status_code=409, detail="租户编码已存在")
        tenant = await TenantDao.create(
            TenantDo(code=data.code, name=data.name, description=data.description),
            request,
        )
        await TenantDao.add_member(
            tenant.id,
            int(request.state.user_id),
            True,
            request,
        )
        return tenant

    @staticmethod
    async def update(tenant_id: int, data, request: Request) -> None:
        """按版本号更新租户。"""
        if not await TenantDao.update_tenant(
            tenant_id,
            data.model_dump(exclude_unset=True, exclude={"version"}),
            data.version,
            request,
        ):
            raise HTTPException(status_code=409, detail="租户已被其他请求修改")

    @staticmethod
    async def delete(tenant_id: int, version: int, request: Request) -> None:
        """按版本号软删除租户。"""
        if tenant_id == settings.DEFAULT_TENANT_ID:
            raise HTTPException(status_code=400, detail="默认租户不能删除")
        if not await TenantDao.soft_delete(tenant_id, version, request):
            raise HTTPException(status_code=409, detail="租户已被其他请求修改")

    @staticmethod
    async def members(tenant_id: int, request: Request):
        """查询租户成员。"""
        if await TenantDao.get(tenant_id, request) is None:
            raise HTTPException(status_code=404, detail="租户不存在")
        return await TenantDao.list_members(tenant_id, request)

    @staticmethod
    async def add_member(tenant_id: int, data, request: Request):
        """添加租户成员。"""
        if await TenantDao.get(tenant_id, request) is None:
            raise HTTPException(status_code=404, detail="租户不存在")
        user = await request.state.mysql.get(UserDo, data.user_id)
        if (
            user is None
            or str(user.status) != "1"
            or getattr(user, "deleted_at", None) is not None
        ):
            raise HTTPException(status_code=404, detail="用户不存在或已停用")
        return await TenantDao.add_member(
            tenant_id, data.user_id, data.is_default, request
        )

    @staticmethod
    async def update_member(tenant_id: int, user_id: int, data, request: Request):
        """按版本号更新成员状态。"""
        if not await TenantDao.update_member(
            tenant_id,
            user_id,
            data.status,
            data.is_default,
            data.version,
            request,
        ):
            raise HTTPException(status_code=409, detail="成员关系已被其他请求修改")
