"""租户和成员关系数据访问层。"""

from fastapi import Request
from sqlalchemy import update
from sqlmodel import select

from module_admin.entity.do.tenant_do import TenantDo, TenantMemberDo
from module_admin.entity.do.user_do import UserDo
from utils.time_utils import now_utc8_naive


class TenantDao:
    """集中处理租户边界、成员关系和乐观锁写入。"""

    @staticmethod
    async def get(tenant_id: int, request: Request) -> TenantDo | None:
        """查询未删除租户。"""
        result = await request.state.mysql.execute(
            select(TenantDo).where(
                TenantDo.id == tenant_id,
                TenantDo.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    @staticmethod
    async def list_for_user(user_id: int, request: Request) -> list[TenantDo]:
        """查询用户当前可用的全部租户。"""
        result = await request.state.mysql.execute(
            select(TenantDo)
            .join(TenantMemberDo, TenantMemberDo.tenant_id == TenantDo.id)
            .where(
                TenantMemberDo.user_id == user_id,
                TenantMemberDo.status == "1",
                TenantMemberDo.deleted_at.is_(None),
                TenantDo.status == "1",
                TenantDo.deleted_at.is_(None),
            )
            .order_by(TenantMemberDo.is_default.desc(), TenantDo.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(request: Request) -> list[TenantDo]:
        """查询所有未删除租户，供平台管理员管理。"""
        result = await request.state.mysql.execute(
            select(TenantDo).where(TenantDo.deleted_at.is_(None)).order_by(TenantDo.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_member(
        user_id: int, tenant_id: int, request: Request
    ) -> TenantMemberDo | None:
        """查询用户在指定租户中的有效成员关系。"""
        result = await request.state.mysql.execute(
            select(TenantMemberDo).where(
                TenantMemberDo.user_id == user_id,
                TenantMemberDo.tenant_id == tenant_id,
                TenantMemberDo.status == "1",
                TenantMemberDo.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    @staticmethod
    async def create(tenant: TenantDo, request: Request) -> TenantDo:
        """写入租户。"""
        request.state.mysql.add(tenant)
        await request.state.mysql.flush()
        return tenant

    @staticmethod
    async def add_member(
        tenant_id: int, user_id: int, is_default: bool, request: Request
    ) -> TenantMemberDo:
        """创建或恢复成员关系。"""
        mysql = request.state.mysql
        existing_result = await mysql.execute(
            select(TenantMemberDo).where(
                TenantMemberDo.user_id == user_id,
                TenantMemberDo.tenant_id == tenant_id,
            )
        )
        member = existing_result.scalars().first()
        if member is None:
            member = TenantMemberDo(
                user_id=user_id,
                tenant_id=tenant_id,
                is_default=is_default,
            )
            mysql.add(member)
        else:
            member.status = "1"
            member.deleted_at = None
            member.is_default = is_default
            member.version += 1
            member.updated_at = now_utc8_naive()
        if is_default:
            await mysql.execute(
                update(TenantMemberDo)
                .where(
                    TenantMemberDo.user_id == user_id,
                    TenantMemberDo.tenant_id != tenant_id,
                )
                .values(is_default=False, updated_at=now_utc8_naive())
            )
        await mysql.flush()
        return member

    @staticmethod
    async def update_member(
        tenant_id: int,
        user_id: int,
        status: str,
        is_default: bool,
        version: int,
        request: Request,
    ) -> bool:
        """按版本号更新成员关系，返回是否成功。"""
        result = await request.state.mysql.execute(
            update(TenantMemberDo)
            .where(
                TenantMemberDo.tenant_id == tenant_id,
                TenantMemberDo.user_id == user_id,
                TenantMemberDo.version == version,
                TenantMemberDo.deleted_at.is_(None),
            )
            .values(
                status=status,
                is_default=is_default,
                version=version + 1,
                updated_at=now_utc8_naive(),
            )
        )
        if result.rowcount != 1:
            return False
        if is_default:
            await request.state.mysql.execute(
                update(TenantMemberDo)
                .where(
                    TenantMemberDo.user_id == user_id,
                    TenantMemberDo.tenant_id != tenant_id,
                )
                .values(is_default=False, updated_at=now_utc8_naive())
            )
        return True

    @staticmethod
    async def list_members(tenant_id: int, request: Request) -> list[dict]:
        """查询租户成员及用户摘要。"""
        result = await request.state.mysql.execute(
            select(TenantMemberDo, UserDo)
            .join(UserDo, UserDo.id == TenantMemberDo.user_id)
            .where(
                TenantMemberDo.tenant_id == tenant_id,
                TenantMemberDo.deleted_at.is_(None),
                UserDo.deleted_at.is_(None),
            )
            .order_by(UserDo.id)
        )
        return [
            {
                "user_id": member.user_id,
                "tenant_id": member.tenant_id,
                "username": user.username,
                "nickname": user.nickname,
                "status": member.status,
                "is_default": member.is_default,
                "version": member.version,
            }
            for member, user in result.all()
        ]

    @staticmethod
    async def update_tenant(
        tenant_id: int, values: dict, version: int, request: Request
    ) -> bool:
        """按版本号更新租户。"""
        values = {**values, "version": version + 1, "update_time": now_utc8_naive()}
        result = await request.state.mysql.execute(
            update(TenantDo)
            .where(
                TenantDo.id == tenant_id,
                TenantDo.version == version,
                TenantDo.deleted_at.is_(None),
            )
            .values(**values)
        )
        return result.rowcount == 1

    @staticmethod
    async def soft_delete(tenant_id: int, version: int, request: Request) -> bool:
        """软删除租户并使后续切换失效。"""
        result = await request.state.mysql.execute(
            update(TenantDo)
            .where(
                TenantDo.id == tenant_id,
                TenantDo.version == version,
                TenantDo.deleted_at.is_(None),
            )
            .values(
                status="0",
                deleted_at=now_utc8_naive(),
                version=version + 1,
                update_time=now_utc8_naive(),
            )
        )
        return result.rowcount == 1
