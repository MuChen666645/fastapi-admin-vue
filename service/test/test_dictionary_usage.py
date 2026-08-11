"""业务页面使用字典数据接口的回归测试。"""

from test.conftest import app
from types import SimpleNamespace

import anyio

from module_admin.auth.authorization import Auth
from module_admin.dao.dictionary_dao import DictionaryDao
from module_admin.entity.do.dictionary_do import DictDataDo


class ScalarResult:
    """提供 DAO 查询测试所需的最小标量结果。"""

    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class QueryResult:
    """提供 SQLAlchemy Result 的最小测试替身。"""

    def __init__(self, values):
        self.values = values

    def scalars(self):
        return ScalarResult(self.values)


class CapturingSession:
    """记录 DAO 发出的查询，避免单元测试连接真实 MySQL。"""

    def __init__(self, values):
        self.values = values
        self.statement = None

    async def execute(self, statement):
        self.statement = statement
        return QueryResult(self.values)


def test_usable_dictionary_route_requires_login_without_permission_code() -> None:
    route = next(
        route
        for route in app.routes
        if route.path == "/api/v1/dict/data/type/{dict_type}" and "GET" in route.methods
    )
    dependencies = [dependency.call for dependency in route.dependant.dependencies]

    assert Auth.login_status in dependencies
    assert all(
        getattr(dependency, "permission_code", None) is None
        for dependency in dependencies
    )


def test_usable_dictionary_route_publishes_list_response_model() -> None:
    response_schema = app.openapi()["paths"]["/api/v1/dict/data/type/{dict_type}"][
        "get"
    ]["responses"]["200"]["content"]["application/json"]["schema"]

    assert response_schema["$ref"] == (
        "#/components/schemas/ApiResponseDto_list_DictDataDto__"
    )


def test_list_usable_data_filters_tenant_and_enabled_status() -> None:
    async def run() -> None:
        item = DictDataDo(
            dict_code=9,
            tenant_id=7,
            dict_sort=1,
            dict_label="正常",
            dict_value="1",
            dict_type="sys_normal_disable",
        )
        session = CapturingSession([item])
        request = SimpleNamespace(state=SimpleNamespace(mysql=session, tenant_id=7))

        result = await DictionaryDao.list_usable_data("sys_normal_disable", request)

        assert result == [item]
        statement = str(session.statement)
        assert "JOIN dict_types" in statement
        assert "dict_data.tenant_id" in statement
        assert "dict_types.tenant_id" in statement
        assert "dict_data.status" in statement
        assert "dict_types.status" in statement
        assert "ORDER BY dict_data.dict_sort, dict_data.dict_code" in statement

    anyio.run(run)
