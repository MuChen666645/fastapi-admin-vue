from test.conftest import app, create_async_client
from types import SimpleNamespace

import anyio
import pytest
from fastapi_pagination import Params

from module_admin.auth.authorization import Auth
from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import LoginLogDo
from module_admin.entity.dto.log_dto import OnlineQueryDto
from module_admin.service.log_service import LogService
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
        ("/log/login/list", "GET"),
        ("/log/operation/list", "GET"),
        ("/log/exception/list", "GET"),
        ("/log/{log_type}/batch", "DELETE"),
        ("/online/list", "GET"),
        ("/online/token/{token_id}", "DELETE"),
        ("/online/user/{user_id}", "DELETE"),
    }
    assert expected_routes <= routes


def test_login_log_list_endpoint(monkeypatch) -> None:
    async def fake_list(log_type, query, params, request):
        assert log_type == "login"
        assert params.page == 2
        assert params.size == 10
        return {"items": [], "total": 0, "page": 2, "size": 10, "pages": 0}

    async def run() -> None:
        monkeypatch.setattr(LogService, "list_logs", fake_list)
        async with create_async_client() as client:
            response = await client.get("/log/login/list?page=2&size=10")
        assert response.status_code == 200
        assert response.json()["data"]["page"] == 2

    anyio.run(run)


def test_online_list_endpoint() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            response = await client.get("/online/list?page=2&size=10")
        assert response.status_code == 200
        assert response.json()["data"] == {
            "items": [],
            "total": 0,
            "page": 2,
            "size": 10,
            "pages": 0,
        }

    anyio.run(run)


def test_new_endpoints_publish_response_models() -> None:
    paths = app.openapi()["paths"]
    endpoints = {
        ("/log/login/list", "get"),
        ("/log/operation/list", "get"),
        ("/log/exception/list", "get"),
        ("/log/{log_type}/batch", "delete"),
        ("/online/list", "get"),
        ("/online/token/{token_id}", "delete"),
        ("/online/user/{user_id}", "delete"),
    }
    for path, method in endpoints:
        response = paths[path][method]["responses"]["200"]
        assert "content" in response
        assert "schema" in response["content"]["application/json"]


def test_post_list_publishes_page_response_model() -> None:
    response_schema = app.openapi()["paths"]["/post/list"]["get"]["responses"]["200"][
        "content"
    ]["application/json"]["schema"]
    assert (
        response_schema["$ref"] == "#/components/schemas/ApiResponseDto_Page_PostDto__"
    )


def test_paged_list_endpoints_publish_page_response_models() -> None:
    paths = app.openapi()["paths"]
    expected_refs = {
        "/user/list": "#/components/schemas/ApiResponseDto_Page_UserInfoUserDto__",
        "/role/list": "#/components/schemas/ApiResponseDto_Page_RoleListDto__",
        "/post/list": "#/components/schemas/ApiResponseDto_Page_PostDto__",
        "/dict/type/list": "#/components/schemas/ApiResponseDto_Page_DictTypeDto__",
        "/dict/data/list": "#/components/schemas/ApiResponseDto_Page_DictDataDto__",
        "/log/login/list": "#/components/schemas/ApiResponseDto_Page_LoginLogDto__",
        "/log/operation/list": "#/components/schemas/ApiResponseDto_Page_OperationLogDto__",
        "/log/exception/list": "#/components/schemas/ApiResponseDto_Page_ExceptionLogDto__",
        "/online/list": "#/components/schemas/ApiResponseDto_Page_OnlineSessionDto__",
    }
    for path, expected_ref in expected_refs.items():
        response_schema = paths[path]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert response_schema["$ref"] == expected_ref


def test_log_batch_delete_request_body_has_chinese_description() -> None:
    request_body = app.openapi()["paths"]["/log/{log_type}/batch"]["delete"][
        "requestBody"
    ]
    assert request_body["content"]["application/json"]["schema"]["title"] == (
        "批量删除日志请求"
    )
    assert (
        "批量删除"
        in request_body["content"]["application/json"]["schema"]["description"]
    )


def test_online_users_are_filtered_and_paginated(monkeypatch) -> None:
    sessions = [
        {
            "token_id": str(index).zfill(64),
            "user_id": index,
            "username": f"admin-{index}",
            "ip_address": "10.0.0.1" if index < 3 else "10.0.0.2",
        }
        for index in range(5)
    ]

    async def fake_sessions(request):
        return sessions

    async def run() -> None:
        monkeypatch.setattr(Auth, "list_online_tokens", fake_sessions)
        query = OnlineQueryDto(username="admin", ip_address="10.0.0.1")
        result = await LogService.list_online_users(
            query, Params(page=2, size=2), SimpleNamespace()
        )
        assert result.total == 3
        assert [item["user_id"] for item in result.items] == [2]
        assert result.page == 2
        assert result.size == 2
        assert result.pages == 2

    anyio.run(run)


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


def test_force_logout_user_response_structure(monkeypatch) -> None:
    async def fake_revoke(request, user_id):
        assert user_id == 42
        return 3

    async def run() -> None:
        monkeypatch.setattr(Auth, "revoke_user_tokens", fake_revoke)
        async with create_async_client() as client:
            response = await client.delete("/online/user/42")
        assert response.status_code == 200
        assert response.json()["data"] == {
            "user_id": 42,
            "revoked_token_count": 3,
        }

    anyio.run(run)


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
