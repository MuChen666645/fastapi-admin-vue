"""Integration coverage for the real MySQL, Redis, and HTTP stack."""

import os
import uuid
from dataclasses import dataclass
from test.conftest import app

import anyio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from starlette.requests import Request

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.organization_dao import OrganizationDao
from module_admin.entity.dto.organization_dto import DepartmentUpdateDto
from module_admin.entity.do.log_do import (ExceptionLogDo, LoginLogDo,
                                           OperationLogDo)
from module_admin.entity.do.organization_do import DepartmentDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo, RoleMenuDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo
from utils.fastapi_admin import FastApiAdmin

pytestmark = pytest.mark.integration


@dataclass(frozen=True)
class ResetPasswordCase:
    department_id: int
    admin_user_id: int
    target_user_id: int
    role_id: int
    created_role: bool
    created_wildcard: bool


def _request_for_token() -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [(b"user-agent", b"integration-test")],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 3000),
            "app": app,
        }
    )


def _phone_number() -> str:
    return f"139{uuid.uuid4().int % 100_000_000:08d}"


async def _seed_reset_password_case(session_factory) -> ResetPasswordCase:
    suffix = uuid.uuid4().hex[:12]
    async with session_factory() as session:
        role_result = await session.execute(
            select(RoleDo)
            .where(RoleDo.code == settings.ADMIN_ROLE_CODE, RoleDo.status == "1")
            .order_by(RoleDo.id)
            .limit(1)
        )
        admin_role = role_result.scalars().first()
        created_role = admin_role is None
        if admin_role is None:
            admin_role = RoleDo(
                id=None,
                name=f"integration-admin-{suffix}",
                code=settings.ADMIN_ROLE_CODE,
                description="integration administrator",
            )
            session.add(admin_role)
            await session.flush()

        wildcard_result = await session.execute(
            select(PermissionDo).where(PermissionDo.code == "*:*:*").limit(1)
        )
        wildcard = wildcard_result.scalars().first()
        created_wildcard = wildcard is None
        if wildcard is None:
            session.add(
                PermissionDo(
                    id=None,
                    name="integration wildcard",
                    code="*:*:*",
                    module="system",
                )
            )

        department = DepartmentDo(
            dept_name=f"integration-{suffix}",
            ancestors="0",
        )
        session.add(department)
        await session.flush()

        admin_user = UserDo(
            id=None,
            username=f"integration-admin-{suffix}",
            password=FastApiAdmin.password_hash("old-admin-password"),
            phone=_phone_number(),
            dept_id=department.dept_id,
            role_id=admin_role.id,
            nickname="integration-admin",
        )
        target_user = UserDo(
            id=None,
            username=f"integration-target-{suffix}",
            password=FastApiAdmin.password_hash("old-target-password"),
            phone=_phone_number(),
            dept_id=department.dept_id,
            nickname="integration-target",
        )
        session.add_all([admin_user, target_user])
        await session.commit()

        return ResetPasswordCase(
            department_id=department.dept_id,
            admin_user_id=admin_user.id,
            target_user_id=target_user.id,
            role_id=admin_role.id,
            created_role=created_role,
            created_wildcard=created_wildcard,
        )


async def _cleanup_reset_password_case(session_factory, case: ResetPasswordCase) -> None:
    user_ids = [case.admin_user_id, case.target_user_id]
    async with session_factory() as session:
        await session.execute(delete(LoginLogDo).where(LoginLogDo.user_id.in_(user_ids)))
        await session.execute(
            delete(OperationLogDo).where(OperationLogDo.user_id.in_(user_ids))
        )
        await session.execute(
            delete(ExceptionLogDo).where(ExceptionLogDo.user_id.in_(user_ids))
        )
        await session.execute(delete(UserRoleDo).where(UserRoleDo.user_id.in_(user_ids)))
        await session.execute(delete(UserDo).where(UserDo.id.in_(user_ids)))
        if case.created_role:
            await session.execute(
                delete(RoleMenuDo).where(RoleMenuDo.role_id == case.role_id)
            )
            await session.execute(
                delete(RoleDeptDo).where(RoleDeptDo.role_id == case.role_id)
            )
            await session.execute(delete(RoleDo).where(RoleDo.id == case.role_id))
        await session.execute(
            delete(DepartmentDo).where(DepartmentDo.dept_id == case.department_id)
        )
        if case.created_wildcard:
            await session.execute(
                delete(PermissionDo).where(PermissionDo.code == "*:*:*")
            )
        await session.commit()


def test_reset_password_through_real_services() -> None:
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("RUN_INTEGRATION_TESTS=1 is required")

    async def run() -> None:
        async with app.router.lifespan_context(app):
            app.dependency_overrides.clear()
            case = await _seed_reset_password_case(app.state.mysql_session_factory)
            admin_request = _request_for_token()
            target_request = _request_for_token()
            try:
                await Auth.create_login_token(
                    {"user_id": case.target_user_id, "username": "integration-target"},
                    target_request,
                )
                token = await Auth.create_login_token(
                    {"user_id": case.admin_user_id, "username": "integration-admin"},
                    admin_request,
                )
                async with AsyncClient(
                    transport=ASGITransport(app=app),
                    base_url="http://127.0.0.1",
                ) as client:
                    response = await client.put(
                        f"/user/{case.target_user_id}/reset-password",
                        headers={"Authorization": f"Bearer {token}"},
                        json={"password": "new-target-password"},
                    )

                assert response.status_code == 200, response.text
                assert response.json()["code"] == 200

                async with app.state.mysql_session_factory() as session:
                    target = await session.get(UserDo, case.target_user_id)
                    assert target is not None
                    assert FastApiAdmin.verify_password(
                        "new-target-password", target.password
                    )
                    assert not FastApiAdmin.verify_password(
                        "old-target-password", target.password
                    )
                sessions = await Auth.list_online_tokens(target_request)
                assert all(
                    session["user_id"] != case.target_user_id for session in sessions
                )
            finally:
                await Auth.revoke_user_tokens(admin_request, case.admin_user_id)
                await Auth.revoke_user_tokens(target_request, case.target_user_id)
                await _cleanup_reset_password_case(
                    app.state.mysql_session_factory, case
                )

    anyio.run(run)


def test_department_move_does_not_update_prefix_collision_in_real_mysql() -> None:
    """验证移动部门时不会修改 ID 前缀相同的无关分支。"""

    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("RUN_INTEGRATION_TESTS=1 is required")

    async def run() -> None:
        async with app.router.lifespan_context(app):
            app.dependency_overrides.clear()
            case = await _seed_reset_password_case(app.state.mysql_session_factory)
            admin_request = _request_for_token()
            while True:
                short_id = 100_000 + uuid.uuid4().int % 80_000
                long_id = short_id * 10
                department_ids = [
                    short_id,
                    long_id,
                    short_id + 1,
                    short_id + 2,
                    short_id + 3,
                    long_id + 1,
                ]
                async with app.state.mysql_session_factory() as session:
                    existing = await session.execute(
                        select(DepartmentDo.dept_id).where(
                            DepartmentDo.dept_id.in_(department_ids)
                        )
                    )
                    if not set(existing.scalars().all()):
                        break

            old_parent_id, new_parent_id = short_id + 1, short_id + 2
            moving_child_id = short_id + 3
            unrelated_child_id = long_id + 1
            try:
                async with app.state.mysql_session_factory() as session:
                    session.add_all(
                        [
                            DepartmentDo(
                                dept_id=old_parent_id,
                                parent_id=None,
                                ancestors="0",
                                dept_name="integration-old-parent",
                            ),
                            DepartmentDo(
                                dept_id=new_parent_id,
                                parent_id=None,
                                ancestors="0",
                                dept_name="integration-new-parent",
                            ),
                        ]
                    )
                    await session.flush()
                    session.add_all(
                        [
                            DepartmentDo(
                                dept_id=short_id,
                                parent_id=old_parent_id,
                                ancestors=f"0,{old_parent_id}",
                                dept_name="integration-moving",
                            ),
                            DepartmentDo(
                                dept_id=long_id,
                                parent_id=old_parent_id,
                                ancestors=f"0,{old_parent_id}",
                                dept_name="integration-unrelated",
                            ),
                        ]
                    )
                    await session.flush()
                    session.add_all(
                        [
                            DepartmentDo(
                                dept_id=moving_child_id,
                                parent_id=short_id,
                                ancestors=f"0,{old_parent_id},{short_id}",
                                dept_name="integration-moving-child",
                            ),
                            DepartmentDo(
                                dept_id=unrelated_child_id,
                                parent_id=long_id,
                                ancestors=f"0,{old_parent_id},{long_id}",
                                dept_name="integration-unrelated-child",
                            ),
                        ]
                    )
                    await session.commit()

                admin_request.state.user_id = case.admin_user_id
                async with app.state.mysql_session_factory() as session:
                    admin_request.state.mysql = session
                    result = await OrganizationDao.update_department(
                        short_id,
                        DepartmentUpdateDto(parent_id=new_parent_id),
                        admin_request,
                    )
                    assert result is None
                    await session.commit()

                    records = await session.execute(
                        select(DepartmentDo).where(
                            DepartmentDo.dept_id.in_(department_ids)
                        )
                    )
                    departments = {
                        department.dept_id: department
                        for department in records.scalars().all()
                    }
                    assert departments[short_id].ancestors == f"0,{new_parent_id}"
                    assert departments[moving_child_id].ancestors == (
                        f"0,{new_parent_id},{short_id}"
                    )
                    assert departments[unrelated_child_id].ancestors == (
                        f"0,{old_parent_id},{long_id}"
                    )
            finally:
                async with app.state.mysql_session_factory() as session:
                    for department_id in (
                        moving_child_id,
                        unrelated_child_id,
                        short_id,
                        long_id,
                        new_parent_id,
                        old_parent_id,
                    ):
                        await session.execute(
                            delete(DepartmentDo).where(
                                DepartmentDo.dept_id == department_id
                            )
                        )
                    await session.commit()
                await _cleanup_reset_password_case(
                    app.state.mysql_session_factory, case
                )

    anyio.run(run)
