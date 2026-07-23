"""基于角色的数据权限解析和可复用 SQL 过滤条件。"""

from dataclasses import dataclass

from fastapi import HTTPException, Request
from sqlalchemy import false, func, or_, select, true

from config.env import settings
from module_admin.dao.tenant_scope import current_tenant_id, tenant_clause
from module_admin.entity.do.organization_do import DepartmentDo, PostDo, UserPostDo
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo


@dataclass(frozen=True)
class DataScope:
    """一个操作者所有启用角色的数据权限并集。"""

    actor_user_id: int
    all_data: bool
    department_ids: frozenset[int]
    tenant_id: int | None = None

    def user_id_clause(self, column):
        """为用户 ID 字段构造包含操作者本人的过滤条件。"""
        if self.all_data:
            return true()
        conditions = [column == self.actor_user_id]
        if self.department_ids:
            conditions.append(
                column.in_(
                    select(UserDo.id).where(UserDo.dept_id.in_(self.department_ids))
                )
            )
        return or_(*conditions)

    def department_id_clause(self, column):
        """为部门记录构造数据权限过滤条件。"""
        if self.all_data:
            return true()
        if not self.department_ids:
            return false()
        return column.in_(self.department_ids)

    def post_id_clause(self, column):
        """为分配给可见用户的岗位构造过滤条件。"""
        if self.all_data:
            return true()
        visible_users = select(UserDo.id).where(self.user_id_clause(UserDo.id))
        post_query = select(UserPostDo.post_id).where(
            UserPostDo.user_id.in_(visible_users)
        )
        if self.tenant_id is not None:
            post_query = post_query.where(UserPostDo.tenant_id == self.tenant_id)
        return column.in_(post_query)


class DataScopeService:
    """解析角色数据权限并提供通用访问检查。"""

    # 数据权限编码与数据库种子及 OpenAPI 请求字段保持一致。
    ALL = "1"
    CUSTOM_DEPARTMENT = "2"
    CURRENT_DEPARTMENT = "3"
    DEPARTMENT_AND_CHILDREN = "4"
    SELF = "5"

    @staticmethod
    def _tenant_filter(model, request: Request):
        return tenant_clause(request, model)

    @staticmethod
    def _department_descendant_clause(column, department_id: int):
        """按完整祖先片段匹配部门 ID，避免子串误匹配。"""
        ancestry = func.concat(",", column, ",")
        return ancestry.contains(f",{department_id},")

    @staticmethod
    async def resolve(request: Request) -> DataScope:
        """解析并缓存操作者所有启用角色的数据权限并集。"""
        cached_scope = getattr(request.state, "data_scope", None)
        if cached_scope is not None:
            return cached_scope

        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")

        mysql = request.state.mysql
        tenant_id = current_tenant_id(request)
        legacy_role_id = (
            select(UserDo.role_id).where(UserDo.id == actor_user_id).scalar_subquery()
        )
        assigned_role_ids = select(UserRoleDo.role_id).where(
            UserRoleDo.user_id == actor_user_id,
            UserRoleDo.tenant_id == tenant_id if tenant_id is not None else False,
        )
        role_result = await mysql.execute(
            select(RoleDo).where(
                RoleDo.status == "1",
                DataScopeService._tenant_filter(RoleDo, request),
                or_(RoleDo.id == legacy_role_id, RoleDo.id.in_(assigned_role_ids)),
            )
        )
        roles = list(role_result.scalars().all())
        if any(
            str(role.code).strip().casefold()
            == settings.ADMIN_ROLE_CODE.strip().casefold()
            for role in roles
        ):
            scope = DataScope(
                actor_user_id,
                all_data=True,
                department_ids=frozenset(),
                tenant_id=tenant_id,
            )
            request.state.data_scope = scope
            return scope

        scope_codes = {
            getattr(role, "data_scope", None) or DataScopeService.SELF for role in roles
        }
        department_ids: set[int] = set()

        custom_role_ids = [
            role.id
            for role in roles
            if (getattr(role, "data_scope", None) or DataScopeService.SELF)
            == DataScopeService.CUSTOM_DEPARTMENT
        ]
        if custom_role_ids:
            result = await mysql.execute(
                select(RoleDeptDo.dept_id).where(
                    RoleDeptDo.role_id.in_(custom_role_ids)
                )
            )
            department_ids.update(result.scalars().all())

        current_dept_result = await mysql.execute(
            select(UserDo.dept_id).where(
                UserDo.id == actor_user_id,
                DataScopeService._tenant_filter(UserDo, request),
            )
        )
        current_dept_id = current_dept_result.scalars().first()
        if current_dept_id and DataScopeService.CURRENT_DEPARTMENT in scope_codes:
            department_ids.add(current_dept_id)
        if current_dept_id and DataScopeService.DEPARTMENT_AND_CHILDREN in scope_codes:
            result = await mysql.execute(
                select(DepartmentDo.dept_id).where(
                    DataScopeService._tenant_filter(DepartmentDo, request),
                    or_(
                        DepartmentDo.dept_id == current_dept_id,
                        DataScopeService._department_descendant_clause(
                            DepartmentDo.ancestors, current_dept_id
                        ),
                    ),
                )
            )
            department_ids.update(result.scalars().all())

        scope = DataScope(
            actor_user_id,
            all_data=False,
            department_ids=frozenset(department_ids),
            tenant_id=tenant_id,
        )
        request.state.data_scope = scope
        return scope

    @staticmethod
    async def can_access_user(user_id: int, request: Request) -> bool:
        """检查当前操作者是否可以访问或修改用户。"""
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(UserDo.id).where(
                UserDo.id == user_id,
                DataScopeService._tenant_filter(UserDo, request),
                scope.user_id_clause(UserDo.id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_access_department(dept_id: int, request: Request) -> bool:
        """检查部门是否属于操作者可见的数据范围。"""
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(DepartmentDo.dept_id).where(
                DepartmentDo.dept_id == dept_id,
                DataScopeService._tenant_filter(DepartmentDo, request),
                scope.department_id_clause(DepartmentDo.dept_id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_access_post(post_id: int, request: Request) -> bool:
        """检查岗位是否关联到操作者可见的用户。"""
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(PostDo.post_id).where(
                PostDo.post_id == post_id,
                DataScopeService._tenant_filter(PostDo, request),
                scope.post_id_clause(PostDo.post_id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_mutate_post(post_id: int, request: Request) -> bool:
        """仅当岗位关联的所有用户都在权限范围内时允许写入。"""
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(UserPostDo.user_id)
            .join(PostDo, PostDo.post_id == UserPostDo.post_id)
            .where(
                UserPostDo.post_id == post_id,
                UserPostDo.tenant_id == current_tenant_id(request),
                DataScopeService._tenant_filter(PostDo, request),
            )
        )
        assigned_user_ids = set(result.scalars().all())
        if not assigned_user_ids:
            return False
        visible_user_ids = await DataScopeService.filter_user_ids(
            request, list(assigned_user_ids)
        )
        return visible_user_ids == assigned_user_ids

    @staticmethod
    async def filter_user_ids(request: Request, user_ids: list[int]) -> set[int]:
        """从输入用户 ID 中筛选当前操作者可见的 ID。"""
        unique_user_ids = list(dict.fromkeys(user_ids))
        if not unique_user_ids:
            return set()
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            result = await request.state.mysql.execute(
                select(UserDo.id).where(
                    UserDo.id.in_(unique_user_ids),
                    DataScopeService._tenant_filter(UserDo, request),
                )
            )
            return set(result.scalars().all())
        result = await request.state.mysql.execute(
            select(UserDo.id).where(
                UserDo.id.in_(unique_user_ids),
                DataScopeService._tenant_filter(UserDo, request),
                scope.user_id_clause(UserDo.id),
            )
        )
        return set(result.scalars().all())

    @staticmethod
    async def filter_post_ids(request: Request, post_ids: list[int]) -> set[int]:
        """从输入岗位 ID 中筛选当前操作者可见的 ID。"""
        unique_post_ids = list(dict.fromkeys(post_ids))
        if not unique_post_ids:
            return set()
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            result = await request.state.mysql.execute(
                select(PostDo.post_id).where(
                    PostDo.post_id.in_(unique_post_ids),
                    DataScopeService._tenant_filter(PostDo, request),
                )
            )
            return set(result.scalars().all())
        result = await request.state.mysql.execute(
            select(PostDo.post_id).where(
                PostDo.post_id.in_(unique_post_ids),
                DataScopeService._tenant_filter(PostDo, request),
                scope.post_id_clause(PostDo.post_id),
            )
        )
        return set(result.scalars().all())
