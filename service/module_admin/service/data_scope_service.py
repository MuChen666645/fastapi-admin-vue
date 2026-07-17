"""Role-based data-scope resolution and reusable SQL filters."""

from dataclasses import dataclass

from fastapi import HTTPException, Request
from sqlalchemy import false, func, or_, select, true

from config.env import settings
from module_admin.entity.do.organization_do import (DepartmentDo, PostDo,
                                                    UserPostDo)
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo


@dataclass(frozen=True)
class DataScope:
    """Resolved union of all enabled roles assigned to one actor."""

    actor_user_id: int
    all_data: bool
    department_ids: frozenset[int]

    def user_id_clause(self, column):
        """Build a predicate for a user ID column, including the actor."""
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
        """Build a predicate for department records."""
        if self.all_data:
            return true()
        if not self.department_ids:
            return false()
        return column.in_(self.department_ids)

    def post_id_clause(self, column):
        """Build a predicate for posts assigned to visible users."""
        if self.all_data:
            return true()
        visible_users = select(UserDo.id).where(self.user_id_clause(UserDo.id))
        return column.in_(
            select(UserPostDo.post_id).where(UserPostDo.user_id.in_(visible_users))
        )


class DataScopeService:
    """Resolve role data scope and expose common access checks."""

    ALL = "1"
    CUSTOM_DEPARTMENT = "2"
    CURRENT_DEPARTMENT = "3"
    DEPARTMENT_AND_CHILDREN = "4"
    SELF = "5"

    @staticmethod
    def _department_descendant_clause(column, department_id: int):
        """Match a department ID as a complete ancestry segment."""
        ancestry = func.concat(",", column, ",")
        return ancestry.contains(f",{department_id},")

    @staticmethod
    async def resolve(request: Request) -> DataScope:
        cached_scope = getattr(request.state, "data_scope", None)
        if cached_scope is not None:
            return cached_scope

        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            raise HTTPException(status_code=401, detail="Not Log In")

        mysql = request.state.mysql
        legacy_role_id = (
            select(UserDo.role_id)
            .where(UserDo.id == actor_user_id)
            .scalar_subquery()
        )
        assigned_role_ids = select(UserRoleDo.role_id).where(
            UserRoleDo.user_id == actor_user_id
        )
        role_result = await mysql.execute(
            select(RoleDo).where(
                RoleDo.status == "1",
                or_(RoleDo.id == legacy_role_id, RoleDo.id.in_(assigned_role_ids)),
            )
        )
        roles = list(role_result.scalars().all())
        if any(
            str(role.code).strip().casefold()
            == settings.ADMIN_ROLE_CODE.strip().casefold()
            for role in roles
        ):
            scope = DataScope(actor_user_id, all_data=True, department_ids=frozenset())
            request.state.data_scope = scope
            return scope

        scope_codes = {
            getattr(role, "data_scope", None) or DataScopeService.SELF
            for role in roles
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
            select(UserDo.dept_id).where(UserDo.id == actor_user_id)
        )
        current_dept_id = current_dept_result.scalars().first()
        if current_dept_id and DataScopeService.CURRENT_DEPARTMENT in scope_codes:
            department_ids.add(current_dept_id)
        if current_dept_id and DataScopeService.DEPARTMENT_AND_CHILDREN in scope_codes:
            result = await mysql.execute(
                select(DepartmentDo.dept_id).where(
                    or_(
                        DepartmentDo.dept_id == current_dept_id,
                        DataScopeService._department_descendant_clause(
                            DepartmentDo.ancestors, current_dept_id
                        ),
                    )
                )
            )
            department_ids.update(result.scalars().all())

        scope = DataScope(
            actor_user_id,
            all_data=False,
            department_ids=frozenset(department_ids),
        )
        request.state.data_scope = scope
        return scope

    @staticmethod
    async def can_access_user(user_id: int, request: Request) -> bool:
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(UserDo.id).where(
                UserDo.id == user_id,
                scope.user_id_clause(UserDo.id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_access_department(dept_id: int, request: Request) -> bool:
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(DepartmentDo.dept_id).where(
                DepartmentDo.dept_id == dept_id,
                scope.department_id_clause(DepartmentDo.dept_id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_access_post(post_id: int, request: Request) -> bool:
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(PostDo.post_id).where(
                PostDo.post_id == post_id,
                scope.post_id_clause(PostDo.post_id),
            )
        )
        return result.scalars().first() is not None

    @staticmethod
    async def can_mutate_post(post_id: int, request: Request) -> bool:
        """Allow post writes only when every assigned user is in scope."""
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            return True
        result = await request.state.mysql.execute(
            select(UserPostDo.user_id).where(UserPostDo.post_id == post_id)
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
        unique_user_ids = list(dict.fromkeys(user_ids))
        if not unique_user_ids:
            return set()
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            result = await request.state.mysql.execute(
                select(UserDo.id).where(UserDo.id.in_(unique_user_ids))
            )
            return set(result.scalars().all())
        result = await request.state.mysql.execute(
            select(UserDo.id).where(
                UserDo.id.in_(unique_user_ids),
                scope.user_id_clause(UserDo.id),
            )
        )
        return set(result.scalars().all())

    @staticmethod
    async def filter_post_ids(request: Request, post_ids: list[int]) -> set[int]:
        unique_post_ids = list(dict.fromkeys(post_ids))
        if not unique_post_ids:
            return set()
        scope = await DataScopeService.resolve(request)
        if scope.all_data:
            result = await request.state.mysql.execute(
                select(PostDo.post_id).where(PostDo.post_id.in_(unique_post_ids))
            )
            return set(result.scalars().all())
        result = await request.state.mysql.execute(
            select(PostDo.post_id).where(
                PostDo.post_id.in_(unique_post_ids),
                scope.post_id_clause(PostDo.post_id),
            )
        )
        return set(result.scalars().all())
