"""Integration coverage for the real MySQL, Redis, and HTTP stack."""

import os
from test.conftest import app

import anyio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import delete
from starlette.requests import Request

from module_admin.auth.authorization import Auth
from module_admin.entity.do.log_do import (ExceptionLogDo, LoginLogDo,
                                           OperationLogDo)
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.organization_do import DepartmentDo, UserPostDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo, RoleMenuDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo
from utils.fastapi_admin import FastApiAdmin

pytestmark = pytest.mark.integration


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


async def _seed_reset_password_case(session_factory) -> None:
    ids = {9001, 9002}
    async with session_factory() as session:
        await session.execute(delete(UserPostDo).where(UserPostDo.user_id.in_(ids)))
        await session.execute(delete(UserRoleDo).where(UserRoleDo.user_id.in_(ids)))
        await session.execute(delete(LoginLogDo).where(LoginLogDo.user_id.in_(ids)))
        await session.execute(delete(OperationLogDo).where(OperationLogDo.user_id.in_(ids)))
        await session.execute(delete(ExceptionLogDo).where(ExceptionLogDo.user_id.in_(ids)))
        await session.execute(delete(UserDo).where(UserDo.id.in_(ids)))
        await session.execute(delete(RoleMenuDo).where(RoleMenuDo.role_id.in_(ids)))
        await session.execute(delete(RoleDeptDo).where(RoleDeptDo.role_id.in_(ids)))
        await session.execute(delete(RoleDo).where(RoleDo.id.in_(ids)))
        await session.execute(delete(MenuDo).where(MenuDo.menu_id.in_(ids)))
        await session.execute(delete(PermissionDo).where(PermissionDo.id.in_(ids)))
        await session.execute(delete(DepartmentDo).where(DepartmentDo.dept_id.in_(ids)))

        session.add(DepartmentDo(dept_id=9001, dept_name="integration", ancestors="0"))
        session.add(
            RoleDo(
                id=9001,
                name="integration-admin",
                code="admin",
                description="integration administrator",
            )
        )
        session.add(
            PermissionDo(
                id=9001,
                name="integration wildcard",
                code="*:*:*",
                module="system",
            )
        )
        session.add_all(
            [
                UserDo(
                    id=9001,
                    username="integration-admin",
                    password=FastApiAdmin.password_hash("old-admin-password"),
                    phone="13900009001",
                    dept_id=9001,
                    role_id=9001,
                    nickname="integration-admin",
                ),
                UserDo(
                    id=9002,
                    username="integration-target",
                    password=FastApiAdmin.password_hash("old-target-password"),
                    phone="13900009002",
                    dept_id=9001,
                    nickname="integration-target",
                ),
            ]
        )
        session.add(UserRoleDo(user_id=9001, role_id=9001))
        await session.commit()


def test_reset_password_through_real_services() -> None:
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("RUN_INTEGRATION_TESTS=1 is required")

    async def run() -> None:
        async with app.router.lifespan_context(app):
            app.dependency_overrides.clear()
            await _seed_reset_password_case(app.state.mysql_session_factory)

            await Auth.create_login_token(
                {"user_id": 9002, "username": "integration-target"},
                _request_for_token(),
            )
            token = await Auth.create_login_token(
                {"user_id": 9001, "username": "integration-admin"},
                _request_for_token(),
            )
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://127.0.0.1",
            ) as client:
                response = await client.put(
                    "/user/9002/reset-password",
                    headers={"Authorization": f"Bearer {token}"},
                    json={"password": "new-target-password"},
                )

            assert response.status_code == 200, response.text
            assert response.json()["code"] == 200

            async with app.state.mysql_session_factory() as session:
                target = await session.get(UserDo, 9002)
                assert target is not None
                assert FastApiAdmin.verify_password(
                    "new-target-password", target.password
                )
                assert not FastApiAdmin.verify_password(
                    "old-target-password", target.password
                )
            sessions = await Auth.list_online_tokens(_request_for_token())
            assert all(session["user_id"] != 9002 for session in sessions)

    anyio.run(run)
