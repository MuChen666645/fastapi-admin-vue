from types import SimpleNamespace

import anyio
import pytest
from sqlalchemy import select

from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.organization_do import DepartmentDo, PostDo
from module_admin.entity.do.user_do import UserDo
from module_admin.entity.dto.user_dto import RegisterUserRequestByUsernameDto
from module_admin.service.data_scope_service import DataScope, DataScopeService


def test_user_scope_always_includes_actor_and_allowed_departments() -> None:
    scope = DataScope(
        actor_user_id=7,
        all_data=False,
        department_ids=frozenset({10, 11}),
    )

    statement = select(UserDo).where(scope.user_id_clause(UserDo.id))
    sql = str(statement)

    assert "users.id" in sql
    assert "users.dept_id" in sql
    assert "users.id IN" in sql


def test_post_scope_uses_users_assigned_to_allowed_departments() -> None:
    scope = DataScope(
        actor_user_id=7,
        all_data=False,
        department_ids=frozenset({10}),
    )

    statement = select(PostDo).where(scope.post_id_clause(PostDo.post_id))
    sql = str(statement)

    assert "posts.post_id" in sql
    assert "user_post.post_id" in sql
    assert "users.dept_id" in sql


def test_department_descendant_scope_matches_complete_ids() -> None:
    statement = select(DepartmentDo).where(
        DataScopeService._department_descendant_clause(DepartmentDo.ancestors, 1)
    )
    compiled = statement.compile()

    assert "concat" in str(compiled).lower()
    assert any(",1," in str(value) for value in compiled.params.values())


def test_resolve_uses_custom_role_ids_only() -> None:
    async def run() -> None:
        statements = []

        class Result:
            def __init__(self, values):
                self.values = values

            def scalars(self):
                return self

            def all(self):
                return self.values

            def first(self):
                return self.values[0] if self.values else None

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                sql = str(statement)
                if "FROM roles" in sql:
                    return Result(
                        [
                            SimpleNamespace(id=2, code="operator", data_scope="2"),
                            SimpleNamespace(id=3, code="auditor", data_scope="5"),
                        ]
                    )
                if "role_dept" in sql:
                    return Result([10])
                return Result([])

        request = SimpleNamespace(
            state=SimpleNamespace(user_id=7, mysql=Mysql())
        )
        scope = await DataScopeService.resolve(request)

        assert scope.department_ids == frozenset({10})
        role_dept_statement = next(
            statement for statement in statements if "role_dept" in str(statement)
        )
        assert role_dept_statement.compile().params["role_id_1"] == [2]

    anyio.run(run)


def test_non_all_scope_rejects_user_without_department(monkeypatch) -> None:
    async def run() -> None:
        async def resolve(request):
            return DataScope(
                actor_user_id=7,
                all_data=False,
                department_ids=frozenset(),
            )

        class Mysql:
            def add(self, model):
                raise AssertionError("user should not be created")

        monkeypatch.setattr(DataScopeService, "resolve", resolve)
        request = SimpleNamespace(
            state=SimpleNamespace(user_id=7, mysql=Mysql())
        )
        users = RegisterUserRequestByUsernameDto(
            username="new-user",
            phone="13800138000",
            password="password",
        )

        with pytest.raises(ValueError, match="data scope"):
            await UserDao.create_user_by_username(users, request)

    anyio.run(run)
