""" Role Service. """

from fastapi import HTTPException, Request
from fastapi_pagination import Page, Params

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.role_dao import RoleDao
from module_admin.entity.dto.role_dto import (BatchUpdateRoleStatusDto,
                                              CreateRoleDto, RoleListDto,
                                              UpdataRoleDto)


class RoleService:
    """Role Service."""

    ROLE_PERMISSION_MUTATION_MESSAGE = (
        "Only super administrators can modify role permissions"
    )
    ROLE_SELF_MUTATION_MESSAGE = "Cannot modify a role assigned to the current user"
    VALID_DATA_SCOPES = {"1", "2", "3", "4", "5"}

    @staticmethod
    def _is_admin_code(role_code: str | None) -> bool:
        return bool(
            role_code
            and role_code.strip().casefold()
            == settings.ADMIN_ROLE_CODE.strip().casefold()
        )

    @staticmethod
    def _reject_admin_role(role_code: str | None) -> None:
        if RoleService._is_admin_code(role_code):
            raise HTTPException(status_code=403, detail="超级管理员角色禁止修改")

    @staticmethod
    async def _ensure_role_write_scope(
        request: Request,
        role_ids: list[int] | None = None,
        permission_change: bool = False,
        global_mutation: bool = False,
    ) -> bool:
        """Prevent non-admins from changing effective role permissions."""
        actor_roles = await Auth.get_actor_roles(request)
        if Auth.has_admin_role(actor_roles):
            return True

        if global_mutation:
            raise HTTPException(
                status_code=403,
                detail=RoleService.ROLE_PERMISSION_MUTATION_MESSAGE,
            )

        if permission_change:
            raise HTTPException(
                status_code=403,
                detail=RoleService.ROLE_PERMISSION_MUTATION_MESSAGE,
            )

        actor_role_ids = {role.id for role in actor_roles}
        if actor_role_ids.intersection(role_ids or []):
            raise HTTPException(
                status_code=403,
                detail=RoleService.ROLE_SELF_MUTATION_MESSAGE,
            )
        return False

    @staticmethod
    def _validate_data_scope(
        data_scope: str | None, dept_ids: list[int] | None
    ) -> None:
        if data_scope is not None and data_scope not in RoleService.VALID_DATA_SCOPES:
            raise HTTPException(status_code=400, detail="Invalid data scope")
        if data_scope == "2" and not dept_ids:
            raise HTTPException(
                status_code=400,
                detail="Custom data scope requires at least one department",
            )
        if data_scope is not None and data_scope != "2" and dept_ids:
            raise HTTPException(
                status_code=400,
                detail="Department IDs are only valid for custom data scope",
            )

    @staticmethod
    async def create_role_services(roles: CreateRoleDto, request: Request) -> None:
        """Create role.

        Args:
            roles (CreateRoleDto): 角色模型.
            request (Request): 请求对象.
        """
        RoleService._reject_admin_role(roles.code)
        RoleService._validate_data_scope(roles.data_scope, roles.dept_ids)
        await RoleService._ensure_role_write_scope(
            request,
            permission_change=bool(roles.menu_ids)
            or roles.data_scope != "5"
            or bool(roles.dept_ids),
        )
        try:
            await RoleDao.create_role_by_role_name(roles, request)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return None

    @staticmethod
    async def get_role_by_id_services(role_id: int, request: Request) -> RoleDao:
        """Get role by id.

        Args:
            role_id (int): 角色ID.
            request (Request): 请求对象.

        Returns:
            RoleDao: 角色模型.
        """
        role = await RoleDao.get_role_by_id(role_id, request)
        if role is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        return role

    @staticmethod
    async def get_role_by_name_services(role_name: str, request: Request) -> RoleDao:
        """Get role by name.
        Args:
            role_name (str): 角色名称.
            request (Request): 请求对象.

        Returns:
            RoleDao: 角色模型.
        """
        role = await RoleDao.get_role_by_name(role_name, request)
        if role is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        return role

    @staticmethod
    async def del_role_by_id_services(role_id: int, request: Request) -> None:
        """Delete role by id.

        Args:
            role_id (int): 角色ID.
            request (Request): 请求对象.
        """
        role = await RoleDao.get_role_by_id(role_id, request)
        if role is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        RoleService._reject_admin_role(role["code"])
        await RoleService._ensure_role_write_scope(
            request, [role_id], global_mutation=True
        )
        result = await RoleDao.del_role_by_id(role_id, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def del_role_by_name_services(role_name: str, request: Request) -> None:
        """Delete role by name.

        Args:
            role_name (str): 角色名称.
            request (Request): 请求对象.
        """
        role = await RoleDao.get_role_by_name(role_name, request)
        if role is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        RoleService._reject_admin_role(role.code)
        await RoleService._ensure_role_write_scope(
            request, [role.id], global_mutation=True
        )
        result = await RoleDao.del_role_by_name(role_name, request)
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None

    @staticmethod
    async def upd_role_by_id_services(
        roles: UpdataRoleDto, request: Request, role_id: int
    ) -> None:
        """Update role by id.
        Args:
            roles (UpdataRoleDto): 角色模型.
            request (Request): 请求对象.
            role_id (int): 角色ID.

        Returns:
            RoleDao: 角色模型.
        """
        current_role = await RoleDao.get_role_by_id(role_id, request)
        if current_role is None:
            raise HTTPException(status_code=404, detail="角色不存在")
        RoleService._reject_admin_role(current_role["code"])
        RoleService._reject_admin_role(roles.code)
        effective_data_scope = (
            roles.data_scope
            if roles.data_scope is not None
            else current_role.get("data_scope", "5")
        )
        effective_dept_ids = (
            roles.dept_ids
            if roles.dept_ids is not None
            else current_role.get("dept_ids", [])
        )
        RoleService._validate_data_scope(effective_data_scope, effective_dept_ids)
        await RoleService._ensure_role_write_scope(
            request,
            [role_id],
            permission_change=roles.menu_ids is not None
            or roles.data_scope is not None
            or roles.dept_ids is not None,
        )
        try:
            role = await RoleDao.upd_role_by_id(roles, request, role_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if role is not None:
            raise HTTPException(status_code=404, detail="角色不存在")
        return None

    @staticmethod
    async def get_role_by_all_services(
        request: Request, name: str, code: str, params: Params
    ) -> Page[RoleListDto]:
        """查询角色列表.

        Args:
            request (Request): 请求对象.
            name (str): 角色名称.
            code (str): 角色编码.

        Returns:
            Page[RoleListDto]: 角色列表.
        """
        return await RoleDao.ger_role_by_all(request, name, code, params)

    @staticmethod
    async def batch_update_role_status_services(
        roles: BatchUpdateRoleStatusDto, request: Request
    ) -> None:
        """Batch enable or disable roles."""
        unique_role_ids = list(dict.fromkeys(roles.role_ids))
        role_models = await RoleDao.get_roles_by_ids(unique_role_ids, request)
        role_map = {role.id: role for role in role_models}
        missing_role_ids = [
            role_id for role_id in unique_role_ids if role_id not in role_map
        ]
        if missing_role_ids:
            raise HTTPException(
                status_code=404, detail=f"角色不存在: {missing_role_ids}"
            )
        if any(RoleService._is_admin_code(role.code) for role in role_models):
            raise HTTPException(status_code=403, detail="超级管理员角色禁止修改")
        await RoleService._ensure_role_write_scope(
            request, unique_role_ids, global_mutation=True
        )
        result = await RoleDao.batch_update_role_status(
            unique_role_ids, roles.status, request
        )
        if result is not None:
            raise HTTPException(status_code=404, detail=result)
        return None
