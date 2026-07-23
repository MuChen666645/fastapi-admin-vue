from test.conftest import app
from types import SimpleNamespace

import anyio
import pytest

from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import LoginLogDo
from module_admin.service.user_service import UserService


class FailingSession:
    def __init__(self) -> None:
        self.rollback_called = False
        self.added = None

    def add(self, model) -> None:
        self.added = model

    async def commit(self) -> None:
        raise RuntimeError("commit failed")

    async def rollback(self) -> None:
        self.rollback_called = True

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        return None


def test_log_create_rolls_back_failed_commit() -> None:
    async def run() -> None:
        session = FailingSession()
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(mysql_session_factory=lambda: session)
            )
        )

        with pytest.raises(RuntimeError, match="commit failed"):
            await LogDao.create(LoginLogDo(username="admin", status="1"), request)
        assert session.rollback_called is True

    anyio.run(run)


def test_each_log_create_uses_a_new_session() -> None:
    class SuccessfulSession(FailingSession):
        async def commit(self) -> None:
            return None

    async def run() -> None:
        sessions = []

        def session_factory():
            session = SuccessfulSession()
            sessions.append(session)
            return session

        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(mysql_session_factory=session_factory)
            )
        )
        await LogDao.create(LoginLogDo(username="first", status="1"), request)
        await LogDao.create(LoginLogDo(username="second", status="1"), request)

        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]

    anyio.run(run)


def test_log_and_online_routes_are_registered() -> None:
    routes = {
        (route.path, method)
        for route in app.routes
        for method in getattr(route, "methods", set())
    }
    expected_routes = {
        ("/api/v1/log/login/list", "GET"),
        ("/api/v1/log/operation/list", "GET"),
        ("/api/v1/log/exception/list", "GET"),
        ("/api/v1/log/{log_type}/batch", "DELETE"),
        ("/api/v1/online/list", "GET"),
        ("/api/v1/online/token/{token_id}", "DELETE"),
        ("/api/v1/online/user/{user_id}", "DELETE"),
    }
    assert expected_routes <= routes


def test_new_endpoints_publish_response_models() -> None:
    paths = app.openapi()["paths"]
    endpoints = {
        ("/api/v1/log/login/list", "get"),
        ("/api/v1/log/operation/list", "get"),
        ("/api/v1/log/exception/list", "get"),
        ("/api/v1/log/{log_type}/batch", "delete"),
        ("/api/v1/online/list", "get"),
        ("/api/v1/online/token/{token_id}", "delete"),
        ("/api/v1/online/user/{user_id}", "delete"),
    }
    for path, method in endpoints:
        response = paths[path][method]["responses"]["200"]
        assert "content" in response
        assert "schema" in response["content"]["application/json"]


def test_post_list_publishes_page_response_model() -> None:
    response_schema = app.openapi()["paths"]["/api/v1/post/list"]["get"]["responses"][
        "200"
    ]["content"]["application/json"]["schema"]
    assert (
        response_schema["$ref"] == "#/components/schemas/ApiResponseDto_Page_PostDto__"
    )


def test_paged_list_endpoints_publish_page_response_models() -> None:
    paths = app.openapi()["paths"]
    expected_refs = {
        "/api/v1/user/list": "#/components/schemas/ApiResponseDto_Page_UserInfoUserDto__",
        "/api/v1/role/list": "#/components/schemas/ApiResponseDto_Page_RoleListDto__",
        "/api/v1/post/list": "#/components/schemas/ApiResponseDto_Page_PostDto__",
        "/api/v1/dict/type/list": "#/components/schemas/ApiResponseDto_Page_DictTypeDto__",
        "/api/v1/dict/data/list": "#/components/schemas/ApiResponseDto_Page_DictDataDto__",
        "/api/v1/log/login/list": "#/components/schemas/ApiResponseDto_Page_LoginLogDto__",
        "/api/v1/log/operation/list": "#/components/schemas/ApiResponseDto_Page_OperationLogDto__",
        "/api/v1/log/exception/list": "#/components/schemas/ApiResponseDto_Page_ExceptionLogDto__",
        "/api/v1/online/list": "#/components/schemas/ApiResponseDto_Page_OnlineSessionDto__",
    }
    for path, expected_ref in expected_refs.items():
        response_schema = paths[path]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert response_schema["$ref"] == expected_ref


def test_log_batch_delete_request_body_has_chinese_description() -> None:
    request_body = app.openapi()["paths"]["/api/v1/log/{log_type}/batch"]["delete"][
        "requestBody"
    ]
    assert request_body["content"]["application/json"]["schema"]["title"] == (
        "批量删除日志请求"
    )
    assert (
        "批量删除"
        in request_body["content"]["application/json"]["schema"]["description"]
    )


def test_log_and_online_schemas_have_chinese_field_descriptions() -> None:
    schemas = app.openapi()["components"]["schemas"]
    target_prefixes = (
        "LogQueryDto",
        "LoginLogDto",
        "OperationLogDto",
        "ExceptionLogDto",
        "BatchLogIdsDto",
        "OnlineQueryDto",
        "OnlineSessionDto",
        "ForceLogoutUserResultDto",
    )
    target_schemas = [
        schema for name, schema in schemas.items() if name.startswith(target_prefixes)
    ]
    assert target_schemas
    for schema in target_schemas:
        for field in schema.get("properties", {}).values():
            description = field.get("description", "")
            assert description
            assert any("\u4e00" <= char <= "\u9fff" for char in description)


def test_user_route_tree_uses_frontend_route_shape() -> None:
    class Menu:
        def __init__(self, **kwargs):
            self.data = kwargs

        def model_dump(self):
            return self.data

    routes = UserService._build_route_tree(
        [
            Menu(
                menu_id=1,
                parent_id=0,
                menu_name="system",
                menu_path="/system",
                component="Layout",
                icon="Setting",
                is_hidden="0",
                is_cache="0",
                link_url=None,
                menu_type="C",
            ),
            Menu(
                menu_id=2,
                parent_id=1,
                menu_name="user",
                menu_path="user",
                component="system/user/index",
                icon="User",
                is_hidden="0",
                is_cache="1",
                link_url=None,
                menu_type="C",
            ),
        ]
    )
    assert routes == [
        {
            "path": "/system",
            "name": "system",
            "component": "Layout",
            "redirect": None,
            "hidden": False,
            "meta": {
                "title": "system",
                "icon": "Setting",
                "noCache": True,
                "link": None,
            },
            "children": [
                {
                    "path": "user",
                    "name": "user",
                    "component": "system/user/index",
                    "redirect": None,
                    "hidden": False,
                    "meta": {
                        "title": "user",
                        "icon": "User",
                        "noCache": False,
                        "link": None,
                    },
                    "children": [],
                }
            ],
        }
    ]
