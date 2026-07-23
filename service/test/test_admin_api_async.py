"""基于真实 MySQL、Redis 和 HTTP 栈的后台 API 集成测试。"""

import json
import os
import uuid
from dataclasses import dataclass, field
from test.conftest import app

import anyio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from starlette.requests import Request

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.entity.do.dictionary_do import DictDataDo, DictTypeDo
from module_admin.entity.do.job_do import JobLogDo, ScheduledJobDo
from module_admin.entity.do.log_do import ExceptionLogDo, LoginLogDo, OperationLogDo
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.notice_do import NoticeDo
from module_admin.entity.do.organization_do import DepartmentDo, PostDo, UserPostDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDeptDo, RoleDo, RoleMenuDo
from module_admin.entity.do.system_config_do import SystemConfigDo
from module_admin.entity.do.user_do import UserDo, UserRoleDo
from module_admin.service.code_service import CodeService
from utils.fastapi_admin import FastApiAdmin

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "1",
        reason="RUN_INTEGRATION_TESTS=1 is required for real service tests",
    ),
]

ADMIN_PASSWORD = "integration-admin-password"
CAPTCHA_CODE = "1234"


@dataclass
class ApiCase:
    """记录本次集成测试创建的实体，供清理阶段使用。"""

    suffix: str
    admin_user_id: int
    admin_role_id: int
    department_ids: list[int] = field(default_factory=list)
    user_ids: list[int] = field(default_factory=list)
    post_ids: list[int] = field(default_factory=list)
    menu_ids: list[int] = field(default_factory=list)
    role_ids: list[int] = field(default_factory=list)
    dict_type_ids: list[int] = field(default_factory=list)
    dict_data_ids: list[int] = field(default_factory=list)
    config_ids: list[int] = field(default_factory=list)
    notice_ids: list[int] = field(default_factory=list)
    job_ids: list[int] = field(default_factory=list)
    created_admin_role: bool = False
    created_wildcard: bool = False


def _request_for_token() -> Request:
    """创建用于 Token 清理和验证码哈希的真实请求上下文。"""
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
            "client": ("127.0.0.1", 23456),
            "server": ("127.0.0.1", 3000),
            "app": app,
        }
    )


def _phone_number() -> str:
    """生成本次测试专用的合法手机号。"""
    return f"139{uuid.uuid4().int % 100_000_000:08d}"


async def _seed_case(session_factory) -> ApiCase:
    """使用随机后缀创建真实管理员账号和权限前置数据。"""
    suffix = uuid.uuid4().hex[:12]
    async with session_factory() as session:
        role_result = await session.execute(
            select(RoleDo)
            .where(RoleDo.code == settings.ADMIN_ROLE_CODE, RoleDo.status == "1")
            .order_by(RoleDo.id)
            .limit(1)
        )
        admin_role = role_result.scalars().first()
        created_admin_role = admin_role is None
        if admin_role is None:
            admin_role = RoleDo(
                id=None,
                name=f"integration-admin-{suffix}",
                code=settings.ADMIN_ROLE_CODE,
                description="集成测试管理员角色",
            )
            session.add(admin_role)
            await session.flush()

        wildcard_result = await session.execute(
            select(PermissionDo).where(
                PermissionDo.code == "*:*:*", PermissionDo.status == "1"
            )
        )
        wildcard = wildcard_result.scalars().first()
        created_wildcard = wildcard is None
        if wildcard is None:
            existing_wildcard = await session.execute(
                select(PermissionDo).where(PermissionDo.code == "*:*:*")
            )
            if existing_wildcard.scalars().first() is not None:
                raise RuntimeError("数据库中的超级管理员通配权限已被停用")
            session.add(
                PermissionDo(
                    name="集成测试超级管理员权限",
                    code="*:*:*",
                    module="system",
                )
            )

        department = DepartmentDo(
            dept_name=f"集成测试部门-{suffix}",
            ancestors="0",
        )
        session.add(department)
        await session.flush()

        admin_user = UserDo(
            id=None,
            username=f"integration-admin-{suffix}",
            password=FastApiAdmin.password_hash(ADMIN_PASSWORD),
            phone=_phone_number(),
            email=f"integration-admin-{suffix}@example.com",
            dept_id=department.dept_id,
            role_id=admin_role.id,
            nickname="集成测试管理员",
        )
        session.add(admin_user)
        await session.commit()

        return ApiCase(
            suffix=suffix,
            admin_user_id=admin_user.id,
            admin_role_id=admin_role.id,
            department_ids=[department.dept_id],
            user_ids=[admin_user.id],
            created_admin_role=created_admin_role,
            created_wildcard=created_wildcard,
        )


async def _seed_captcha(captcha_id: str, request: Request) -> None:
    """把已知验证码写入真实 Redis，供登录接口消费。"""
    payload = json.dumps(
        {
            "code_hash": CodeService._code_hash(captcha_id, CAPTCHA_CODE),
            "ip_hash": CodeService._client_ip_hash(request),
            "attempts": 0,
        },
        separators=(",", ":"),
    )
    await app.state.redis.set(
        CodeService._captcha_key(captcha_id),
        payload,
        ex=settings.CAPTCHA_TTL_SECONDS,
    )


def _assert_success(response) -> dict:
    """校验统一成功响应并返回业务数据。"""
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    return body["data"]


async def _find_id(session_factory, model, field, value) -> int:
    """从真实数据库中查询随机测试实体的主键。"""
    async with session_factory() as session:
        result = await session.execute(select(model).where(field == value))
        item = result.scalars().first()
        assert item is not None
        for primary_key in (
            "id",
            "dept_id",
            "post_id",
            "menu_id",
            "dict_id",
            "dict_code",
        ):
            identifier = getattr(item, primary_key, None)
            if identifier is not None:
                return identifier
        raise AssertionError(f"无法读取 {model.__name__} 的主键")


async def _login(client: AsyncClient, case: ApiCase) -> str:
    """通过真实验证码、密码校验和 Redis 锁定服务登录。"""
    captcha_id = uuid.uuid4().hex
    request = _request_for_token()
    await _seed_captcha(captcha_id, request)
    response = await client.post(
        "/api/v1/user/login/username",
        data={
            "username": f"integration-admin-{case.suffix}",
            "password": ADMIN_PASSWORD,
            "captcha_id": captcha_id,
            "captcha": CAPTCHA_CODE,
        },
    )
    data = _assert_success(response)
    assert data["access_token"]
    return data["access_token"]


async def _cleanup_case(session_factory, case: ApiCase) -> None:
    """按外键依赖顺序删除本次测试创建的所有业务数据。"""
    request = _request_for_token()
    for session in await Auth.list_online_tokens(request):
        if session.get("user_id") in case.user_ids:
            await Auth._delete_cache_key(
                request, f"{Auth.TOKEN_REDIS_PREFIX}{session['token_id']}"
            )

    async with session_factory() as session:
        if case.user_ids:
            await session.execute(
                delete(LoginLogDo).where(LoginLogDo.user_id.in_(case.user_ids))
            )
            await session.execute(
                delete(OperationLogDo).where(OperationLogDo.user_id.in_(case.user_ids))
            )
            await session.execute(
                delete(ExceptionLogDo).where(ExceptionLogDo.user_id.in_(case.user_ids))
            )
            await session.execute(
                delete(UserPostDo).where(UserPostDo.user_id.in_(case.user_ids))
            )
            await session.execute(
                delete(UserRoleDo).where(UserRoleDo.user_id.in_(case.user_ids))
            )
            await session.execute(delete(UserDo).where(UserDo.id.in_(case.user_ids)))
        if case.job_ids:
            await session.execute(
                delete(JobLogDo).where(JobLogDo.job_id.in_(case.job_ids))
            )
            await session.execute(
                delete(ScheduledJobDo).where(ScheduledJobDo.id.in_(case.job_ids))
            )
        if case.menu_ids:
            await session.execute(
                delete(RoleMenuDo).where(RoleMenuDo.menu_id.in_(case.menu_ids))
            )
            await session.execute(
                delete(MenuDo).where(MenuDo.menu_id.in_(case.menu_ids))
            )
        if case.dict_data_ids:
            await session.execute(
                delete(DictDataDo).where(DictDataDo.dict_code.in_(case.dict_data_ids))
            )
        if case.dict_type_ids:
            await session.execute(
                delete(DictTypeDo).where(DictTypeDo.dict_id.in_(case.dict_type_ids))
            )
        if case.notice_ids:
            await session.execute(
                delete(NoticeDo).where(NoticeDo.id.in_(case.notice_ids))
            )
        if case.config_ids:
            await session.execute(
                delete(SystemConfigDo).where(SystemConfigDo.id.in_(case.config_ids))
            )
        if case.post_ids:
            await session.execute(
                delete(UserPostDo).where(UserPostDo.post_id.in_(case.post_ids))
            )
            await session.execute(
                delete(PostDo).where(PostDo.post_id.in_(case.post_ids))
            )
        if case.department_ids:
            for department_id in sorted(case.department_ids, reverse=True):
                await session.execute(
                    delete(DepartmentDo).where(DepartmentDo.dept_id == department_id)
                )
        if case.created_admin_role:
            await session.execute(
                delete(RoleDeptDo).where(RoleDeptDo.role_id == case.admin_role_id)
            )
            await session.execute(delete(RoleDo).where(RoleDo.id == case.admin_role_id))
        if case.role_ids:
            await session.execute(
                delete(RoleMenuDo).where(RoleMenuDo.role_id.in_(case.role_ids))
            )
            await session.execute(
                delete(RoleDeptDo).where(RoleDeptDo.role_id.in_(case.role_ids))
            )
            await session.execute(delete(RoleDo).where(RoleDo.id.in_(case.role_ids)))
        if case.created_wildcard:
            await session.execute(
                delete(PermissionDo).where(PermissionDo.code == "*:*:*")
            )
        await session.commit()


async def _run_with_admin(callback) -> None:
    """启动真实应用、执行测试回调，并保证测试数据最终清理。"""
    async with app.router.lifespan_context(app):
        app.dependency_overrides.clear()
        case = await _seed_case(app.state.mysql_session_factory)
        try:
            transport = ASGITransport(
                app=app,
                client=("127.0.0.1", 23456),
            )
            async with AsyncClient(
                transport=transport,
                base_url="http://127.0.0.1",
            ) as client:
                token = await _login(client, case)
                client.headers["Authorization"] = f"Bearer {token}"
                await callback(client, case)
        finally:
            await _cleanup_case(app.state.mysql_session_factory, case)


def test_real_captcha_and_user_api() -> None:
    """验证真实验证码、登录、用户查询、创建、更新和删除链路。"""

    async def run() -> None:
        async def exercise(client: AsyncClient, case: ApiCase) -> None:
            image = await client.get("/api/v1/captcha/image")
            assert image.status_code == 200
            assert image.json()["data"]["captcha_id"]
            assert image.json()["data"]["image"].startswith("data:image/")

            username = f"integration-target-{case.suffix}"
            phone = _phone_number()
            _assert_success(
                await client.post(
                    "/api/v1/user/add",
                    json={
                        "username": username,
                        "password": "target-password",
                        "phone": phone,
                        "email": f"{username}@example.com",
                        "nickname": "集成测试用户",
                        "sex": "1",
                    },
                )
            )
            user_id = await _find_id(
                app.state.mysql_session_factory, UserDo, UserDo.username, username
            )
            case.user_ids.append(user_id)

            info = _assert_success(await client.get("/api/v1/user/info"))
            assert info["user"]["username"] == f"integration-admin-{case.suffix}"
            assert "*:*:*" in info["permissions"]
            routes = _assert_success(await client.get("/api/v1/user/routes"))
            assert isinstance(routes, list)
            users = _assert_success(
                await client.get("/api/v1/user/list", params={"username": username})
            )
            assert users["total"] == 1
            assert users["items"][0]["id"] == user_id

            _assert_success(
                await client.put(
                    f"/api/v1/user/{user_id}",
                    json={"nickname": "集成测试用户已更新"},
                )
            )
            invalid_update = await client.put(
                f"/api/v1/user/{user_id}", json={"role_id": case.admin_role_id}
            )
            assert invalid_update.status_code == 422
            _assert_success(await client.delete(f"/api/v1/user/{user_id}"))
            assert (await client.get(f"/api/v1/user/{user_id}")).status_code == 404

        await _run_with_admin(exercise)

    anyio.run(run)


def test_real_admin_crud_and_monitoring_api() -> None:
    """验证角色、菜单、组织、字典、参数、公告、任务和日志真实链路。"""

    async def run() -> None:
        async def exercise(client: AsyncClient, case: ApiCase) -> None:
            suffix = case.suffix

            department_name = f"集成子部门-{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/dept/add",
                    json={
                        "dept_name": department_name,
                        "parent_id": case.department_ids[0],
                    },
                )
            )
            department_id = await _find_id(
                app.state.mysql_session_factory,
                DepartmentDo,
                DepartmentDo.dept_name,
                department_name,
            )
            case.department_ids.append(department_id)
            _assert_success(
                await client.put(
                    f"/api/v1/dept/{department_id}",
                    json={"dept_name": f"{department_name}-已更新"},
                )
            )

            post_code = f"integration-post-{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/post/add",
                    json={"post_code": post_code, "post_name": "集成测试岗位"},
                )
            )
            post_id = await _find_id(
                app.state.mysql_session_factory, PostDo, PostDo.post_code, post_code
            )
            case.post_ids.append(post_id)
            _assert_success(
                await client.put(
                    f"/api/v1/post/{post_id}", json={"post_name": "集成测试岗位已更新"}
                )
            )

            role_code = f"integration-role-{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/role/add",
                    json={"name": f"集成角色-{suffix}", "code": role_code},
                )
            )
            role_id = await _find_id(
                app.state.mysql_session_factory, RoleDo, RoleDo.code, role_code
            )
            case.role_ids.append(role_id)
            _assert_success(
                await client.put(
                    f"/api/v1/role/{role_id}",
                    json={"name": f"集成角色-{suffix}-已更新"},
                )
            )

            menu_name = f"集成菜单-{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/menu/add",
                    json={
                        "menu_name": menu_name,
                        "parent_id": 0,
                        "menu_type": "C",
                        "menu_path": f"/integration-{suffix}",
                        "sort": 1,
                        "component": "Layout",
                        "is_cache": "0",
                        "is_hidden": "0",
                    },
                )
            )
            menu_id = await _find_id(
                app.state.mysql_session_factory, MenuDo, MenuDo.menu_name, menu_name
            )
            case.menu_ids.append(menu_id)
            _assert_success(
                await client.put(
                    f"/api/v1/menu/{menu_id}",
                    json={"menu_name": f"{menu_name}-已更新"},
                )
            )

            dict_type = f"integration_dict_{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/dict/type/add",
                    json={"dict_name": "集成字典", "dict_type": dict_type},
                )
            )
            dict_type_id = await _find_id(
                app.state.mysql_session_factory,
                DictTypeDo,
                DictTypeDo.dict_type,
                dict_type,
            )
            case.dict_type_ids.append(dict_type_id)
            _assert_success(
                await client.post(
                    "/api/v1/dict/data/add",
                    json={
                        "dict_label": "集成值",
                        "dict_value": "1",
                        "dict_type": dict_type,
                    },
                )
            )
            dict_data_id = await _find_id(
                app.state.mysql_session_factory,
                DictDataDo,
                DictDataDo.dict_type,
                dict_type,
            )
            case.dict_data_ids.append(dict_data_id)
            _assert_success(
                await client.put(f"/api/v1/dict/data/{dict_data_id}", json={"status": "0"})
            )

            config_key = f"integration.config.{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/config/add",
                    json={
                        "config_name": "集成参数",
                        "config_key": config_key,
                        "config_value": "before",
                    },
                )
            )
            config_id = await _find_id(
                app.state.mysql_session_factory,
                SystemConfigDo,
                SystemConfigDo.config_key,
                config_key,
            )
            case.config_ids.append(config_id)
            _assert_success(
                await client.put(
                    f"/api/v1/config/{config_id}",
                    json={"config_value": "after"},
                )
            )
            config_value = _assert_success(
                await client.get(f"/api/v1/config/value/{config_key}")
            )
            assert config_value["config_value"] == "after"

            notice_title = f"集成公告-{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/notice/add",
                    json={
                        "notice_title": notice_title,
                        "notice_content": "集成测试公告内容",
                    },
                )
            )
            notice_id = await _find_id(
                app.state.mysql_session_factory,
                NoticeDo,
                NoticeDo.notice_title,
                notice_title,
            )
            case.notice_ids.append(notice_id)
            _assert_success(
                await client.put(
                    f"/api/v1/notice/{notice_id}",
                    json={"notice_content": "公告已更新"},
                )
            )

            job_key = f"integration.job.{suffix}"
            _assert_success(
                await client.post(
                    "/api/v1/job/add",
                    json={
                        "job_name": "集成任务",
                        "job_key": job_key,
                        "task_name": "integration.noop",
                        "cron_expression": "*/5 * * * *",
                        "args_json": "{}",
                    },
                )
            )
            job_id = await _find_id(
                app.state.mysql_session_factory,
                ScheduledJobDo,
                ScheduledJobDo.job_key,
                job_key,
            )
            case.job_ids.append(job_id)
            _assert_success(
                await client.put(
                    f"/api/v1/job/{job_id}",
                    json={"job_name": "集成任务已更新"},
                )
            )
            logs = _assert_success(await client.get(f"/api/v1/job/{job_id}/log/list"))
            assert logs["total"] == 0
            run_response = await client.post(f"/api/v1/job/{job_id}/run")
            assert run_response.status_code in {200, 503}
            if run_response.status_code == 200:
                assert run_response.json()["data"]["status"] == "failed"

            for path in (
                "/api/v1/role/list",
                "/api/v1/menu/list",
                "/api/v1/dept/list",
                "/api/v1/post/list",
                "/api/v1/dict/type/list",
                "/api/v1/dict/data/list",
                "/api/v1/config/list",
                "/api/v1/notice/list",
                "/api/v1/job/list",
                "/api/v1/log/login/list",
                "/api/v1/log/operation/list",
                "/api/v1/online/list",
            ):
                assert _assert_success(await client.get(path)) is not None

            _assert_success(await client.delete(f"/api/v1/notice/{notice_id}"))
            _assert_success(await client.delete(f"/api/v1/config/{config_id}"))
            _assert_success(await client.delete(f"/api/v1/job/{job_id}"))
            _assert_success(await client.delete(f"/api/v1/dict/data/{dict_data_id}"))
            _assert_success(await client.delete(f"/api/v1/dict/type/{dict_type_id}"))
            _assert_success(await client.delete(f"/api/v1/menu/{menu_id}"))
            _assert_success(await client.delete(f"/api/v1/role/{role_id}"))
            _assert_success(await client.delete(f"/api/v1/post/{post_id}"))
            _assert_success(await client.delete(f"/api/v1/dept/{department_id}"))

        await _run_with_admin(exercise)

    anyio.run(run)
