from pathlib import Path
from types import SimpleNamespace

import anyio
import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from config.mysql_serve import MysqlServe
from interceptors.http_intercept import ApiExceptionInterception
from middleware.response_intercept import ResponseInterceptor
from module_admin.auth.authorization import Auth
from module_admin.dao.role_dao import RoleCodeConflictError, RoleDao
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.role_do import RoleDo
from module_admin.entity.dto.role_dto import CreateRoleDto
from module_admin.entity.dto.user_dto import (
    LoginUserRequestByPhoneDto,
    LoginUserRequestByUsernameDto,
)
from module_admin.service.code_service import CodeService
from module_admin.service.login_security_service import LoginSecurityService
from module_admin.service.user_service import UserService
from utils.fastapi_admin import FastApiAdmin


def make_request() -> SimpleNamespace:
    return SimpleNamespace(
        client=SimpleNamespace(host="198.51.100.20"),
        headers={},
        state=SimpleNamespace(),
    )


def test_disabled_users_cannot_get_tokens_from_either_login_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_user_by_username(*args, **kwargs):
            return SimpleNamespace(
                id=1,
                username="disabled-user",
                password="hashed-password",
                status="0",
            )

        async def get_user_by_phone(*args, **kwargs):
            return SimpleNamespace(
                id=1,
                username="disabled-user",
                password="hashed-password",
                status="0",
            )

        async def no_op(*args, **kwargs):
            return None

        async def unexpected_token(*args, **kwargs):
            raise AssertionError("disabled users must not receive a token")

        monkeypatch.setattr(UserDao, "get_user_by_username", get_user_by_username)
        monkeypatch.setattr(UserDao, "get_user_by_phone", get_user_by_phone)
        monkeypatch.setattr(FastApiAdmin, "verify_password", lambda *args: True)
        monkeypatch.setattr(CodeService, "verify_captcha_services", no_op)
        monkeypatch.setattr(LoginSecurityService, "clear_password_failures", no_op)
        monkeypatch.setattr(UserService, "_ensure_login_ip_allowed", no_op)
        monkeypatch.setattr(UserService, "_record_login", no_op)
        monkeypatch.setattr(Auth, "create_login_token", unexpected_token)

        username_login = LoginUserRequestByUsernameDto(
            username="disabled-user",
            password="password",
            captcha_id="captcha-id-1234567890",
            captcha="1234",
        )
        phone_login = LoginUserRequestByPhoneDto(
            phone="13800138000",
            password="password",
            captcha_id="captcha-id-1234567890",
            captcha="1234",
        )

        for login in (username_login, phone_login):
            with pytest.raises(HTTPException) as exception:
                if isinstance(login, LoginUserRequestByUsernameDto):
                    await UserService.get_user_by_username_services(login, make_request())
                else:
                    await UserService.get_user_by_phone_services(login, make_request())
            assert exception.value.status_code == 403
            assert exception.value.detail == "用户已停用"

    anyio.run(run)


def test_mysql_url_preserves_special_characters() -> None:
    configured = SimpleNamespace(
        MYSQL_USERNAME="user@example",
        MYSQL_PASSWORD="p@ss:/with?reserved",
        MYSQL_HOST="mysql.example",
        MYSQL_POST=3306,
        MYSQL_DATABASES="admin_db",
    )

    url = MysqlServe.get_db_url(configured)

    assert url.drivername == "mysql+aiomysql"
    assert url.username == configured.MYSQL_USERNAME
    assert url.password == configured.MYSQL_PASSWORD
    assert url.host == configured.MYSQL_HOST
    assert url.port == configured.MYSQL_POST
    assert url.database == configured.MYSQL_DATABASES
    assert "user%40example:p%40ss%3A%2Fwith%3Freserved@" in url.render_as_string(
        hide_password=False
    )


def test_create_role_requires_name_and_code() -> None:
    with pytest.raises(ValidationError):
        CreateRoleDto()

    assert RoleDo.__table__.columns["code"].unique is True


def test_role_dao_rejects_duplicate_code_before_insert() -> None:
    class Result:
        def scalar_one_or_none(self):
            return 10

    class Session:
        async def execute(self, statement):
            return Result()

        def add(self, role):
            raise AssertionError("duplicate role must not be inserted")

    request = SimpleNamespace(state=SimpleNamespace(mysql=Session()))
    role = CreateRoleDto(name="Operator", code="operator")

    async def run() -> None:
        with pytest.raises(RoleCodeConflictError, match="角色编码已存在"):
            await RoleDao.create_role_by_role_name(role, request)

    anyio.run(run)


def test_captcha_font_path_is_independent_of_working_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    async def run() -> None:
        monkeypatch.chdir(tmp_path)
        image = await FastApiAdmin.CaptchaGenerator("1234").create_captcha()
        assert image.startswith("data:image/png;base64,")

    anyio.run(run)


def test_validation_errors_keep_field_details() -> None:
    app = FastAPI()
    ApiExceptionInterception(app)
    app.add_middleware(ResponseInterceptor)

    @app.get("/validate")
    async def validate(value: int):
        return {"value": value}

    async def run() -> None:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get("/validate", params={"value": "invalid"})

        body = response.json()
        assert response.status_code == 422
        assert body["code"] == 422
        assert body["message"][0]["loc"] == ["query", "value"]
        assert body["message"][0]["type"] == "int_parsing"

    anyio.run(run)


def test_role_code_unique_migration_is_headed_after_existing_migrations() -> None:
    migration = Path("alembic/versions/0004_role_code_unique.py").read_text(
        encoding="utf-8"
    )

    assert 'revision = "0004_role_code_unique"' in migration
    assert 'down_revision = "0003_admin_operations"' in migration
    assert 'op.create_index("uq_roles_code", "roles", ["code"], unique=True)' in migration
