import anyio
import pytest

from module_admin.service.code_service import CodeService
from module_admin.service.menu_service import MenuService
from module_admin.service.role_service import RoleService
from module_admin.service.user_service import UserService
from module_admin.service.organization_service import (
    DepartmentService,
    PostService,
)
from module_admin.service.dictionary_service import DictionaryService
from test.conftest import create_async_client


def run_async(async_fn):
    anyio.run(async_fn)


def ok_response(response):
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    return body["data"]


@pytest.fixture(autouse=True)
def mock_services(monkeypatch: pytest.MonkeyPatch) -> None:
    async def none_service(*args, **kwargs):
        return None

    async def token_service(*args, **kwargs):
        return {"access_token": "test-token"}

    async def user_list_service(*args, **kwargs):
        return {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}

    async def user_routes_service(*args, **kwargs):
        return [
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
                "children": [],
            }
        ]

    async def user_info_service(*args, **kwargs):
        return {
            "user": {
                "id": 1,
                "create_time": "2026-07-13T00:00:00",
                "username": "admin",
                "email": "admin@example.com",
                "phone": "13800138000",
                "role_id": 1,
                "nickname": "admin",
                "sex": "1",
                "avatar": "",
                "update_time": "2026-07-13T00:00:00",
                "status": "1",
            },
            "roles": [
                {
                    "id": 1,
                    "name": "admin",
                    "code": "admin",
                    "description": "administrator",
                    "create_time": "2026-07-13T00:00:00",
                    "update_time": "2026-07-13T00:00:00",
                    "status": "1",
                }
            ],
            "permissions": ["*:*:*"],
        }

    async def captcha_image_service(*args, **kwargs):
        return {
            "captcha_id": "captcha-id-1234567890",
            "image": "data:image/png;base64,test",
        }

    async def role_detail_service(*args, **kwargs):
        return {
            "id": 1,
            "name": "admin",
            "code": "admin",
            "description": "administrator",
            "create_time": "2026-07-13T00:00:00",
            "update_time": "2026-07-13T00:00:00",
            "status": "1",
            "menu_ids": [1, 2],
        }

    async def role_list_service(*args, **kwargs):
        return {
            "items": [await role_detail_service()],
            "total": 1,
            "page": 1,
            "size": 50,
            "pages": 1,
        }

    async def menu_detail_service(*args, **kwargs):
        return {
            "menu_id": 1,
            "menu_name": "system",
            "parent_id": 0,
            "icon": "Setting",
            "menu_path": "/system",
            "component": "Layout",
            "is_hidden": "0",
            "is_cache": "0",
            "menu_type": "C",
            "sort": 1,
            "link_url": None,
            "perms": "system:menu:list",
            "status": "1",
            "create_time": "2026-07-13T00:00:00",
            "update_time": "2026-07-13T00:00:00",
            "remark": "system menu",
        }

    async def menu_list_service(*args, **kwargs):
        menu = await menu_detail_service()
        menu["children"] = []
        return [menu]

    monkeypatch.setattr(CodeService, "get_captcha_img_services", captcha_image_service)
    monkeypatch.setattr(CodeService, "verify_captcha_services", none_service)

    monkeypatch.setattr(UserService, "create_user_by_username_services", none_service)
    monkeypatch.setattr(UserService, "get_user_by_username_services", token_service)
    monkeypatch.setattr(UserService, "get_user_by_phone_services", token_service)
    monkeypatch.setattr(UserService, "list_users_services", user_list_service)
    monkeypatch.setattr(UserService, "get_current_user_routes_services", user_routes_service)
    monkeypatch.setattr(UserService, "get_current_user_info_services", user_info_service)
    monkeypatch.setattr(UserService, "get_user_by_id_services", user_info_service)
    monkeypatch.setattr(UserService, "update_user_by_id_services", none_service)
    monkeypatch.setattr(UserService, "update_user_password_by_id_services", none_service)
    monkeypatch.setattr(UserService, "bind_user_roles_services", none_service)
    monkeypatch.setattr(UserService, "batch_update_user_status_services", none_service)
    monkeypatch.setattr(UserService, "batch_delete_users_services", none_service)
    monkeypatch.setattr(UserService, "delete_user_by_id_services", none_service)
    monkeypatch.setattr(UserService, "logout_services", none_service)

    monkeypatch.setattr(RoleService, "create_role_services", none_service)
    monkeypatch.setattr(RoleService, "get_role_by_all_services", role_list_service)
    monkeypatch.setattr(RoleService, "get_role_by_id_services", role_detail_service)
    monkeypatch.setattr(RoleService, "del_role_by_id_services", none_service)
    monkeypatch.setattr(RoleService, "upd_role_by_id_services", none_service)
    monkeypatch.setattr(RoleService, "batch_update_role_status_services", none_service)

    monkeypatch.setattr(MenuService, "create_menu_by_router", none_service)
    monkeypatch.setattr(MenuService, "create_menu_by_btn", none_service)
    monkeypatch.setattr(MenuService, "create_menu_by_link", none_service)
    monkeypatch.setattr(MenuService, "create_menu_by_iframe", none_service)
    monkeypatch.setattr(MenuService, "get_menu_list_all", menu_list_service)
    monkeypatch.setattr(MenuService, "get_menu_by_id_services", menu_detail_service)
    monkeypatch.setattr(MenuService, "upd_menu_by_id_services", none_service)
    monkeypatch.setattr(MenuService, "del_menu_by_id_services", none_service)

    async def list_service(*args, **kwargs):
        return []

    async def detail_service(*args, **kwargs):
        return {"id": 1}

    async def post_list_service(*args, **kwargs):
        return {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}

    async def page_list_service(*args, **kwargs):
        return {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}

    monkeypatch.setattr(DepartmentService, "list", list_service)
    monkeypatch.setattr(DepartmentService, "detail", detail_service)
    monkeypatch.setattr(DepartmentService, "create", none_service)
    monkeypatch.setattr(DepartmentService, "update", none_service)
    monkeypatch.setattr(DepartmentService, "delete", none_service)

    monkeypatch.setattr(PostService, "list", post_list_service)
    monkeypatch.setattr(PostService, "detail", detail_service)
    monkeypatch.setattr(PostService, "create", none_service)
    monkeypatch.setattr(PostService, "update", none_service)
    monkeypatch.setattr(PostService, "delete", none_service)

    monkeypatch.setattr(DictionaryService, "list_types", page_list_service)
    monkeypatch.setattr(DictionaryService, "type_detail", detail_service)
    monkeypatch.setattr(DictionaryService, "create_type", none_service)
    monkeypatch.setattr(DictionaryService, "update_type", none_service)
    monkeypatch.setattr(DictionaryService, "delete_type", none_service)
    monkeypatch.setattr(DictionaryService, "list_data", page_list_service)
    monkeypatch.setattr(DictionaryService, "data_detail", detail_service)
    monkeypatch.setattr(DictionaryService, "create_data", none_service)
    monkeypatch.setattr(DictionaryService, "update_data", none_service)
    monkeypatch.setattr(DictionaryService, "delete_data", none_service)


def test_captcha_api_async() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            image = ok_response(await client.get("/captcha/image"))
            number = await client.get("/captcha/number")
            verified = ok_response(
                await client.get(
                    "/captcha/verify",
                    params={
                        "captcha_id": "captcha-id-1234567890",
                        "code": "1234",
                    },
                )
            )

        assert image == {
            "captcha_id": "captcha-id-1234567890",
            "image": "data:image/png;base64,test",
        }
        assert number.status_code == 410
        assert number.json() == {
            "code": 410,
            "message": "数字验证码接口已停用，请使用图形验证码",
            "data": None,
        }
        assert verified is None

    run_async(run)


def test_user_api_async() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            ok_response(
                await client.post(
                    "/user/add",
                    json={
                        "username": "tester",
                        "password": "password",
                        "phone": "13800138000",
                        "email": "tester@example.com",
                        "nickname": "tester",
                        "sex": "1",
                    },
                )
            )
            username_login = ok_response(
                await client.post(
                    "/user/login/username",
                    data={
                        "username": "tester",
                        "password": "password",
                        "captcha_id": "captcha-id-1234567890",
                        "captcha": "1234",
                    },
                )
            )
            phone_login = ok_response(
                await client.post(
                    "/user/login/phone",
                    data={
                        "phone": "13800138000",
                        "password": "password",
                        "captcha_id": "captcha-id-1234567890",
                        "captcha": "1234",
                    },
                )
            )
            phone_login_without_password = await client.post(
                "/user/login/phone",
                data={
                    "phone": "13800138000",
                    "captcha_id": "captcha-id-1234567890",
                    "captcha": "1234",
                },
            )
            ok_response(await client.post("/user/logout"))
            users = ok_response(
                await client.get(
                    "/user/list",
                    params={
                        "username": "admin",
                        "phone": "138",
                        "email": "admin@example.com",
                        "nickname": "admin",
                    },
                )
            )
            current_user = ok_response(await client.get("/user/info"))
            routes = ok_response(await client.get("/user/routes"))
            user = ok_response(await client.get("/user/1"))
            ok_response(
                await client.put(
                    "/user/1",
                    json={
                        "username": "tester",
                        "phone": "13800138000",
                        "email": "tester@example.com",
                        "sex": "1",
                        "status": "1",
                    },
                )
            )
            update_with_role_id = await client.put(
                "/user/1", json={"role_id": 1}
            )
            ok_response(
                await client.put(
                    "/user/1/password",
                    json={"old_password": "old-password", "new_password": "new-password"},
                )
            )
            ok_response(
                await client.put("/user/1/roles", json={"role_ids": [1, 2]})
            )
            ok_response(
                await client.put(
                    "/user/batch/status",
                    json={"user_ids": [1, 2], "status": "0"},
                )
            )
            ok_response(
                await client.request(
                    "DELETE", "/user/batch", json={"user_ids": [1, 2]}
                )
            )
            ok_response(await client.delete("/user/1"))

        assert username_login == {"access_token": "test-token"}
        assert phone_login == {"access_token": "test-token"}
        assert phone_login_without_password.status_code == 422
        assert update_with_role_id.status_code == 422
        assert users == {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}
        assert current_user["user"]["id"] == 1
        assert routes[0]["meta"]["title"] == "system"
        assert routes[0]["children"] == []
        assert user["permissions"] == ["*:*:*"]

    run_async(run)


def test_role_api_async() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            ok_response(
                await client.post(
                    "/role/add",
                    json={
                        "name": "admin",
                        "code": "admin",
                        "description": "administrator",
                        "menu_ids": [1, 2],
                    },
                )
            )
            roles = ok_response(
                await client.get("/role/list", params={"name": "admin", "code": "admin"})
            )
            role = ok_response(await client.get("/role/1"))
            ok_response(
                await client.put(
                    "/role/1",
                    json={
                        "name": "admin",
                        "code": "admin",
                        "description": "administrator",
                        "menu_ids": [1, 3],
                    },
                )
            )
            ok_response(
                await client.put(
                    "/role/batch/status",
                    json={"role_ids": [1, 2], "status": "0"},
                )
            )
            ok_response(await client.delete("/role/1"))

        assert roles["total"] == 1
        assert role["id"] == 1
        assert role["menu_ids"] == [1, 2]

    run_async(run)


def test_menu_api_async() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            ok_response(
                await client.post(
                    "/menu/add",
                    json={
                        "menu_name": "system",
                        "parent_id": 0,
                        "menu_type": "C",
                        "menu_path": "/system",
                        "sort": 1,
                        "icon": "Setting",
                        "component": "Layout",
                        "is_cache": "0",
                        "is_hidden": "0",
                        "remark": "system menu",
                    },
                )
            )
            invalid_menu = await client.post(
                "/menu/add",
                json={
                    "menu_name": "invalid",
                    "parent_id": 0,
                    "menu_type": "F",
                    "menu_path": "/invalid",
                },
            )
            menus = ok_response(
                await client.get(
                    "/menu/list", params={"menu_name": "system", "status": "1"}
                )
            )
            menu = ok_response(await client.get("/menu/1"))
            ok_response(
                await client.put(
                    "/menu/1",
                    json={
                        "menu_name": "system",
                        "parent_id": 0,
                        "menu_type": "C",
                        "menu_path": "/system",
                        "sort": 1,
                        "status": "1",
                    },
                )
            )
            ok_response(await client.delete("/menu/1"))

        assert menus[0]["menu_id"] == 1
        assert menu["menu_name"] == "system"
        assert invalid_menu.status_code == 422

    run_async(run)


def test_organization_and_dictionary_api_async() -> None:
    async def run() -> None:
        async with create_async_client() as client:
            ok_response(await client.get("/dept/list", params={"status": "1"}))
            ok_response(await client.get("/dept/1"))
            ok_response(
                await client.post(
                    "/dept/add", json={"dept_name": "研发部", "parent_id": 0}
                )
            )
            ok_response(await client.put("/dept/1", json={"dept_name": "技术部"}))
            ok_response(await client.delete("/dept/1"))

            posts = ok_response(await client.get("/post/list", params={"status": "1"}))
            ok_response(await client.get("/post/1"))
            ok_response(
                await client.post(
                    "/post/add",
                    json={"post_code": "dev", "post_name": "开发工程师"},
                )
            )
            ok_response(await client.put("/post/1", json={"post_name": "高级开发"}))
            ok_response(await client.delete("/post/1"))

            dict_types = ok_response(await client.get("/dict/type/list"))
            ok_response(await client.get("/dict/type/1"))
            ok_response(
                await client.post(
                    "/dict/type/add",
                    json={"dict_name": "用户性别", "dict_type": "sys_user_sex"},
                )
            )
            ok_response(await client.put("/dict/type/1", json={"status": "0"}))
            ok_response(await client.delete("/dict/type/1"))

            dict_data = ok_response(
                await client.get(
                    "/dict/data/list", params={"dict_type": "sys_user_sex"}
                )
            )
            ok_response(await client.get("/dict/data/1"))
            ok_response(
                await client.post(
                    "/dict/data/add",
                    json={
                        "dict_label": "男",
                        "dict_value": "1",
                        "dict_type": "sys_user_sex",
                    },
                )
            )
            ok_response(await client.put("/dict/data/1", json={"status": "0"}))
            ok_response(await client.delete("/dict/data/1"))

        assert posts == {"items": [], "total": 0, "page": 1, "size": 50, "pages": 0}
        assert dict_types == {
            "items": [],
            "total": 0,
            "page": 1,
            "size": 50,
            "pages": 0,
        }
        assert dict_data == {
            "items": [],
            "total": 0,
            "page": 1,
            "size": 50,
            "pages": 0,
        }

    run_async(run)
