from test.conftest import app
from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from module_admin.dao.menu_dao import MenuDao
from module_admin.dao.role_dao import RoleDao
from module_admin.dao.user_dao import UserDao
from module_admin.entity.dto.menu_dto import CreateMenuByButtonDto, UpdMenuDto
from module_admin.entity.dto.role_dto import (
    BatchUpdateRoleStatusDto,
    CreateRoleDto,
    UpdataRoleDto,
)
from module_admin.entity.dto.user_dto import (
    BatchUpdateUserStatusDto,
    BatchUserIdsDto,
    BindUserRolesDto,
    LoginUserRequestByPhoneDto,
    ResetUserPasswordRequestDto,
    UpdateUserPasswordRequestDto,
    UpdateUserRequestDto,
)
from module_admin.service.code_service import CodeService
from module_admin.service.menu_service import MenuService
from module_admin.service.role_service import RoleService
from module_admin.service.user_service import UserService
from utils.fastapi_admin import FastApiAdmin


def make_request(user_id: int | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        app=app,
        client=SimpleNamespace(host="198.51.100.20"),
        headers={"user-agent": "pytest"},
        state=SimpleNamespace(user_id=user_id),
    )


def make_role(role_id: int, code: str, status: str = "1") -> SimpleNamespace:
    return SimpleNamespace(id=role_id, code=code, status=status)


def test_numeric_captcha_service_fails_closed() -> None:
    async def run() -> None:
        with pytest.raises(HTTPException) as exception:
            await CodeService.get_captcha_num_services(SimpleNamespace())

        assert exception.value.status_code == 410
        assert "停用" in exception.value.detail

    anyio.run(run)


def test_phone_login_requires_password_and_user_update_rejects_role_id() -> None:
    with pytest.raises(ValidationError):
        LoginUserRequestByPhoneDto(
            phone="13800138000",
            captcha_id="captcha-id-1234567890",
            captcha="1234",
        )

    with pytest.raises(ValidationError):
        UpdateUserRequestDto(username="operator", role_id=1)


def test_phone_login_rejects_wrong_password_before_captcha(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        captcha_verified = False

        async def get_user(*args, **kwargs):
            return SimpleNamespace(
                id=2,
                username="operator",
                phone="13800138000",
                password="hashed-password",
            )

        async def verify_captcha(*args, **kwargs):
            nonlocal captcha_verified
            captcha_verified = True

        async def record_login(*args, **kwargs):
            return None

        monkeypatch.setattr(UserDao, "get_user_by_phone", get_user)
        monkeypatch.setattr(FastApiAdmin, "verify_password", lambda *args: False)
        monkeypatch.setattr(CodeService, "verify_captcha_services", verify_captcha)
        monkeypatch.setattr(UserService, "_record_login", record_login)

        users = LoginUserRequestByPhoneDto(
            phone="13800138000",
            password="wrong-password",
            captcha_id="captcha-id-1234567890",
            captcha="1234",
        )
        with pytest.raises(HTTPException) as exception:
            await UserService.get_user_by_phone_services(users, make_request())

        assert exception.value.status_code == 401
        assert exception.value.detail == "密码错误"
        assert captcha_verified is False

    anyio.run(run)


def test_non_admin_cannot_grant_admin_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        bind_called = False

        async def get_user(*args, **kwargs):
            return SimpleNamespace(id=20)

        async def get_roles_by_ids(*args, **kwargs):
            return [make_role(1, "admin")]

        async def get_user_roles(user_id, *args, **kwargs):
            if user_id == 10:
                return [make_role(2, "operator")]
            return []

        async def get_admin_user_ids(*args, **kwargs):
            return set()

        async def bind_roles(*args, **kwargs):
            nonlocal bind_called
            bind_called = True

        monkeypatch.setattr(UserDao, "get_user_by_id", get_user)
        monkeypatch.setattr(UserDao, "get_roles_by_ids", get_roles_by_ids)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "get_admin_user_ids", get_admin_user_ids)
        monkeypatch.setattr(UserDao, "bind_user_roles", bind_roles)

        with pytest.raises(HTTPException) as exception:
            await UserService.bind_user_roles_services(
                20,
                BindUserRolesDto(role_ids=[1]),
                make_request(user_id=10),
            )

        assert exception.value.status_code == 403
        assert exception.value.detail == "禁止授予超级管理员角色"
        assert bind_called is False

    anyio.run(run)


def test_non_admin_can_only_grant_roles_they_own(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_user(*args, **kwargs):
            return SimpleNamespace(id=20)

        async def get_roles_by_ids(*args, **kwargs):
            return [make_role(3, "auditor")]

        async def get_user_roles(user_id, *args, **kwargs):
            if user_id == 10:
                return [make_role(2, "operator")]
            return []

        async def get_admin_user_ids(*args, **kwargs):
            return set()

        monkeypatch.setattr(UserDao, "get_user_by_id", get_user)
        monkeypatch.setattr(UserDao, "get_roles_by_ids", get_roles_by_ids)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "get_admin_user_ids", get_admin_user_ids)

        with pytest.raises(HTTPException) as exception:
            await UserService.bind_user_roles_services(
                20,
                BindUserRolesDto(role_ids=[3]),
                make_request(user_id=10),
            )

        assert exception.value.status_code == 403
        assert exception.value.detail == "无权授予角色: [3]"

    anyio.run(run)


def test_non_admin_cannot_modify_admin_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_user(*args, **kwargs):
            return SimpleNamespace(id=20)

        async def get_roles_by_ids(*args, **kwargs):
            return [make_role(2, "operator")]

        async def get_user_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def get_admin_user_ids(*args, **kwargs):
            return {20}

        monkeypatch.setattr(UserDao, "get_user_by_id", get_user)
        monkeypatch.setattr(UserDao, "get_roles_by_ids", get_roles_by_ids)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "get_admin_user_ids", get_admin_user_ids)

        with pytest.raises(HTTPException) as exception:
            await UserService.bind_user_roles_services(
                20,
                BindUserRolesDto(role_ids=[2]),
                make_request(user_id=10),
            )

        assert exception.value.status_code == 403
        assert exception.value.detail == UserService.ADMIN_USER_PROTECTION_MESSAGE

    anyio.run(run)


@pytest.mark.parametrize(
    "operation",
    [
        "update",
        "password",
        "reset",
        "batch_status",
        "batch_delete",
        "delete",
    ],
)
def test_non_admin_cannot_mutate_admin_user_through_any_user_write_service(
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    async def run() -> None:
        mutation_called = False

        async def get_user_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def get_admin_user_ids(user_ids, *args, **kwargs):
            assert 20 in user_ids
            return {20}

        async def get_user(*args, **kwargs):
            return SimpleNamespace(id=20, password="hashed-password")

        async def mutate(*args, **kwargs):
            nonlocal mutation_called
            mutation_called = True

        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "get_admin_user_ids", get_admin_user_ids)
        monkeypatch.setattr(UserDao, "get_user_by_id", get_user)
        monkeypatch.setattr(UserDao, "update_user_by_id", mutate)
        monkeypatch.setattr(UserDao, "update_user_password_by_id", mutate)
        monkeypatch.setattr(UserDao, "batch_update_user_status", mutate)
        monkeypatch.setattr(UserDao, "batch_delete_users", mutate)
        monkeypatch.setattr(UserDao, "delete_user_by_id", mutate)

        request = make_request(user_id=10)
        with pytest.raises(HTTPException) as exception:
            if operation == "update":
                await UserService.update_user_by_id_services(
                    20,
                    UpdateUserRequestDto(nickname="admin"),
                    request,
                )
            elif operation == "password":
                await UserService.update_user_password_by_id_services(
                    20,
                    UpdateUserPasswordRequestDto(
                        old_password="old-password",
                        new_password="new-password",
                    ),
                    request,
                )
            elif operation == "reset":
                await UserService.reset_user_password_services(
                    20,
                    ResetUserPasswordRequestDto(password="new-password"),
                    request,
                )
            elif operation == "batch_status":
                await UserService.batch_update_user_status_services(
                    BatchUpdateUserStatusDto(user_ids=[20, 21], status="0"),
                    request,
                )
            elif operation == "batch_delete":
                await UserService.batch_delete_users_services(
                    BatchUserIdsDto(user_ids=[20, 21]),
                    request,
                )
            else:
                await UserService.delete_user_by_id_services(20, request)

        assert exception.value.status_code == 403
        assert exception.value.detail == UserService.ADMIN_USER_PROTECTION_MESSAGE
        assert mutation_called is False

    anyio.run(run)


def test_admin_can_manage_admin_user(monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> None:
        mutation_called = False

        async def get_user_roles(*args, **kwargs):
            return [make_role(1, "admin")]

        async def get_admin_user_ids(*args, **kwargs):
            raise AssertionError("Admin actors do not require target role lookup")

        async def update_user(*args, **kwargs):
            nonlocal mutation_called
            mutation_called = True

        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "get_admin_user_ids", get_admin_user_ids)
        monkeypatch.setattr(UserDao, "update_user_by_id", update_user)

        await UserService.update_user_by_id_services(
            20,
            UpdateUserRequestDto(nickname="admin"),
            make_request(user_id=1),
        )
        assert mutation_called is True

    anyio.run(run)


def test_admin_user_lookup_covers_current_and_legacy_role_relations() -> None:
    async def run() -> None:
        statements = []

        class Result:
            @staticmethod
            def scalars():
                return SimpleNamespace(all=lambda: [])

        class Mysql:
            @staticmethod
            async def execute(statement):
                statements.append(str(statement))
                return Result()

        request = SimpleNamespace(state=SimpleNamespace(mysql=Mysql()))
        assert await UserDao.get_admin_user_ids([1, 2], request) == set()
        assert len(statements) == 1
        assert "UNION" in statements[0]
        assert "user_role" in statements[0]
        assert "users" in statements[0]

    anyio.run(run)


def test_admin_can_assign_any_enabled_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        assigned_role_ids = None

        async def get_user(*args, **kwargs):
            return SimpleNamespace(id=20)

        async def get_roles_by_ids(*args, **kwargs):
            return [make_role(3, "auditor")]

        async def get_user_roles(*args, **kwargs):
            return [make_role(1, "admin")]

        async def bind_roles(user_id, role_ids, request):
            nonlocal assigned_role_ids
            assigned_role_ids = role_ids

        monkeypatch.setattr(UserDao, "get_user_by_id", get_user)
        monkeypatch.setattr(UserDao, "get_roles_by_ids", get_roles_by_ids)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(UserDao, "bind_user_roles", bind_roles)

        await UserService.bind_user_roles_services(
            20,
            BindUserRolesDto(role_ids=[3]),
            make_request(user_id=10),
        )

        assert assigned_role_ids == [3]

    anyio.run(run)


def test_non_admin_cannot_change_role_permissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        update_called = False

        async def get_role(*args, **kwargs):
            return {"id": 2, "code": "operator", "menu_ids": [10]}

        async def get_user_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def update_role(*args, **kwargs):
            nonlocal update_called
            update_called = True

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(RoleDao, "upd_role_by_id", update_role)

        with pytest.raises(HTTPException) as exception:
            await RoleService.upd_role_by_id_services(
                UpdataRoleDto(menu_ids=[11]),
                make_request(user_id=10),
                role_id=2,
            )

        assert exception.value.status_code == 403
        assert exception.value.detail == RoleService.ROLE_PERMISSION_MUTATION_MESSAGE
        assert update_called is False

    anyio.run(run)


def test_admin_can_change_role_permissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        update_called = False

        async def get_role(*args, **kwargs):
            return {"id": 2, "code": "operator", "menu_ids": [10]}

        async def get_user_roles(*args, **kwargs):
            return [make_role(1, "admin")]

        async def update_role(*args, **kwargs):
            nonlocal update_called
            update_called = True

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(RoleDao, "upd_role_by_id", update_role)

        await RoleService.upd_role_by_id_services(
            UpdataRoleDto(menu_ids=[11]),
            make_request(user_id=1),
            role_id=2,
        )

        assert update_called is True

    anyio.run(run)


def test_non_admin_cannot_change_role_data_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        update_called = False

        async def get_role(*args, **kwargs):
            return {"id": 2, "code": "operator", "menu_ids": [], "data_scope": "5"}

        async def get_user_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def update_role(*args, **kwargs):
            nonlocal update_called
            update_called = True

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(RoleDao, "upd_role_by_id", update_role)

        with pytest.raises(HTTPException) as exception:
            await RoleService.upd_role_by_id_services(
                UpdataRoleDto(data_scope="1"),
                make_request(user_id=10),
                role_id=2,
            )

        assert exception.value.status_code == 403
        assert exception.value.detail == RoleService.ROLE_PERMISSION_MUTATION_MESSAGE
        assert update_called is False

    anyio.run(run)


def test_custom_role_data_scope_requires_departments() -> None:
    with pytest.raises(HTTPException) as exception:
        RoleService._validate_data_scope("2", [])
    assert exception.value.status_code == 400


def test_role_data_scope_partial_update_keeps_existing_departments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        update_called = False

        async def get_role(*args, **kwargs):
            return {
                "id": 2,
                "code": "operator",
                "menu_ids": [],
                "data_scope": "2",
                "dept_ids": [10],
            }

        async def get_user_roles(*args, **kwargs):
            return [make_role(1, "admin")]

        async def update_role(*args, **kwargs):
            nonlocal update_called
            update_called = True

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(RoleDao, "upd_role_by_id", update_role)

        await RoleService.upd_role_by_id_services(
            UpdataRoleDto(dept_ids=[11]),
            make_request(user_id=1),
            role_id=2,
        )

        assert update_called is True

    anyio.run(run)


def test_non_admin_cannot_mutate_button_permission_menu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_user_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def get_menu(*args, **kwargs):
            return SimpleNamespace(menu_type="F")

        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)
        monkeypatch.setattr(MenuDao, "get_menu_by_id", get_menu)

        request = make_request(user_id=10)
        with pytest.raises(HTTPException) as update_exception:
            await MenuService.upd_menu_by_id_services(
                10,
                UpdMenuDto(perms="system:user:remove"),
                request,
            )

        with pytest.raises(HTTPException) as create_exception:
            await MenuService.create_menu_by_btn(
                CreateMenuByButtonDto(
                    menu_name="new-button",
                    parent_id=1,
                    perms="system:user:remove",
                    menu_type="F",
                    sort=1,
                    remark="test",
                ),
                request,
            )

        with pytest.raises(HTTPException) as delete_exception:
            await MenuService.del_menu_by_id_services(10, request)

        assert update_exception.value.status_code == 403
        assert create_exception.value.status_code == 403
        assert delete_exception.value.status_code == 403
        assert (
            update_exception.value.detail
            == MenuService.BUTTON_PERMISSION_MUTATION_MESSAGE
        )

    anyio.run(run)


def test_admin_role_code_is_reserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        create_dto = CreateRoleDto(
            name="another admin",
            code="ADMIN",
            description="reserved",
        )
        with pytest.raises(HTTPException) as create_exception:
            await RoleService.create_role_services(create_dto, make_request())
        assert create_exception.value.status_code == 403

        async def get_role(*args, **kwargs):
            return {"id": 2, "code": "operator", "menu_ids": []}

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        update_dto = UpdataRoleDto(code=" admin ")
        with pytest.raises(HTTPException) as update_exception:
            await RoleService.upd_role_by_id_services(
                update_dto, make_request(), role_id=2
            )
        assert update_exception.value.status_code == 403

    anyio.run(run)


def test_existing_admin_role_cannot_be_deleted_or_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_role(*args, **kwargs):
            return {"id": 1, "code": "admin", "menu_ids": []}

        async def get_roles(*args, **kwargs):
            return [make_role(1, "admin")]

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(RoleDao, "get_roles_by_ids", get_roles)

        with pytest.raises(HTTPException) as delete_exception:
            await RoleService.del_role_by_id_services(1, make_request())
        assert delete_exception.value.status_code == 403

        with pytest.raises(HTTPException) as status_exception:
            await RoleService.batch_update_role_status_services(
                BatchUpdateRoleStatusDto(role_ids=[1], status="0"),
                make_request(),
            )
        assert status_exception.value.status_code == 403

    anyio.run(run)


def test_non_admin_cannot_change_global_role_lifecycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def get_role(*args, **kwargs):
            return {"id": 2, "code": "operator", "menu_ids": []}

        async def get_roles(*args, **kwargs):
            return [make_role(2, "operator")]

        async def get_user_roles(*args, **kwargs):
            return [make_role(3, "auditor")]

        monkeypatch.setattr(RoleDao, "get_role_by_id", get_role)
        monkeypatch.setattr(RoleDao, "get_roles_by_ids", get_roles)
        monkeypatch.setattr(UserDao, "get_user_roles", get_user_roles)

        with pytest.raises(HTTPException) as delete_exception:
            await RoleService.del_role_by_id_services(2, make_request(user_id=10))
        with pytest.raises(HTTPException) as status_exception:
            await RoleService.batch_update_role_status_services(
                BatchUpdateRoleStatusDto(role_ids=[2], status="0"),
                make_request(user_id=10),
            )

        assert delete_exception.value.status_code == 403
        assert status_exception.value.status_code == 403

    anyio.run(run)
