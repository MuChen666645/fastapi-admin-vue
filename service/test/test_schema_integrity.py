from datetime import timedelta
from types import SimpleNamespace

import anyio
from sqlmodel import SQLModel

from module_admin.dao.organization_dao import OrganizationDao
from module_admin.entity.do.role_do import RoleDo
from module_admin.entity.do.user_do import UserDo
from module_admin.entity.dto.organization_dto import DepartmentCreateDto
from utils.time_utils import now_utc8, now_utc8_naive


def test_relationships_define_expected_foreign_keys() -> None:
    foreign_keys = {
        (table.name, key.parent.name, key.target_fullname, key.ondelete)
        for table in SQLModel.metadata.tables.values()
        for key in table.foreign_keys
    }

    assert {
        ("users", "role_id", "roles.id", "SET NULL"),
        ("users", "dept_id", "departments.dept_id", "RESTRICT"),
        ("user_role", "user_id", "users.id", "CASCADE"),
        ("user_role", "role_id", "roles.id", "CASCADE"),
        ("role_menu", "role_id", "roles.id", "CASCADE"),
        ("role_menu", "menu_id", "menu.menu_id", "CASCADE"),
        ("user_post", "user_id", "users.id", "CASCADE"),
        ("user_post", "post_id", "posts.post_id", "RESTRICT"),
        ("departments", "parent_id", "departments.dept_id", "RESTRICT"),
        ("menu", "parent_id", "menu.menu_id", "CASCADE"),
        ("login_logs", "user_id", "users.id", "SET NULL"),
        ("operation_logs", "user_id", "users.id", "SET NULL"),
        ("exception_logs", "user_id", "users.id", "SET NULL"),
    } <= foreign_keys


def test_user_and_role_time_defaults_use_factories() -> None:
    assert UserDo.model_fields["create_time"].default_factory is now_utc8_naive
    assert RoleDo.model_fields["create_time"].default_factory is now_utc8_naive
    assert RoleDo.model_fields["update_time"].default_factory is now_utc8_naive


def test_application_time_helpers_use_utc8() -> None:
    aware_time = now_utc8()
    stored_time = now_utc8_naive()

    assert aware_time.utcoffset() == timedelta(hours=8)
    assert stored_time.tzinfo is None
    assert abs((stored_time - aware_time.replace(tzinfo=None)).total_seconds()) < 1


def test_root_department_is_stored_with_null_parent() -> None:
    class FakeSession:
        def __init__(self) -> None:
            self.added = None

        def add(self, model) -> None:
            self.added = model

    async def run() -> None:
        session = FakeSession()
        request = SimpleNamespace(state=SimpleNamespace(mysql=session))
        result = await OrganizationDao.create_department(
            DepartmentCreateDto(parent_id=0, dept_name="根部门"), request
        )

        assert result is None
        assert session.added.parent_id is None
        assert session.added.ancestors == "0"

    anyio.run(run)
