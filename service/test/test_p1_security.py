"""P1 安全边界和运维生命周期回归测试。"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse

import anyio
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi_pagination import Params
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from config.env import settings
from middleware.idempotency_middleware import IdempotencyMiddleware
from module_admin.auth.authorization import Auth
from module_admin.controller.backup_controller import (
    BackupController,
    BackupRestoreRequestDto,
)
from module_admin.dao.permission_dao import PermissionDao
from module_admin.dao.system_config_dao import SystemConfigDao
from module_admin.dao.tenant_dao import TenantDao
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.file_do import FileChunkUploadDo
from module_admin.entity.do.job_do import ScheduledJobDo
from module_admin.entity.do.system_config_do import SystemConfigDo
from module_admin.entity.dto.system_config_dto import (
    SystemConfigCreateDto,
    SystemConfigUpdateDto,
)
from module_admin.service.data_scope_service import DataScope, DataScopeService
from module_admin.service.excel_service import ExcelService
from module_admin.service.external_identity_service import ExternalIdentityService
from module_admin.service.file_service import FileService
from module_admin.service.idempotency_service import IdempotencyService
from module_admin.service.job_scheduler import JobScheduler
from module_admin.service.mfa_service import MfaService
from module_admin.service.system_config_service import SystemConfigService
from module_admin.service.user_service import UserService


class _Result:
    def __init__(self, values=None):
        self.values = list(values or [])

    def scalars(self):
        return self

    def all(self):
        return self.values

    def first(self):
        return self.values[0] if self.values else None


def _request(**state_values):
    return SimpleNamespace(state=SimpleNamespace(**state_values))


def test_user_list_and_batch_mutations_include_tenant_filter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            def __init__(self):
                self.execute_count = 0

            async def execute(self, statement):
                self.execute_count += 1
                statements.append(statement)
                if self.execute_count == 2:
                    return _Result([7])
                return _Result([SimpleNamespace(id=7)])

        async def resolve(_request):
            return DataScope(7, all_data=True, department_ids=frozenset())

        async def paginate(_mysql, query, params, transformer):
            statements.append(query)
            return SimpleNamespace(items=[])

        monkeypatch.setattr(DataScopeService, "resolve", resolve)
        monkeypatch.setattr("module_admin.dao.user_dao.paginate", paginate)
        request = _request(mysql=Mysql(), tenant_id=11)

        await UserDao.list_users(request, None, None, None, None, None, None, Params())
        await UserDao.batch_update_user_status([7], "0", request)
        await UserDao.batch_delete_users([7], request)

        user_queries = [
            str(statement) for statement in statements if "users" in str(statement)
        ]
        assert user_queries
        assert all("tenant_members.tenant_id" in query for query in user_queries)

    anyio.run(run)


def test_oidc_start_uses_nonce_and_pkce(monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> None:
        class Redis:
            def __init__(self):
                self.value = None

            async def set(self, key, value, ex):
                self.value = (key, value, ex)

        names = (
            "OIDC_ENABLED",
            "OIDC_AUTHORIZATION_URL",
            "OIDC_TOKEN_URL",
            "OIDC_USERINFO_URL",
            "OIDC_CLIENT_ID",
            "OIDC_CLIENT_SECRET",
            "OIDC_REDIRECT_URI",
            "OIDC_ISSUER",
            "OIDC_AUDIENCE",
            "OIDC_JWKS_URL",
        )
        original = {name: getattr(settings, name) for name in names}
        for name, value in {
            "OIDC_ENABLED": True,
            "OIDC_AUTHORIZATION_URL": "https://issuer.example/authorize",
            "OIDC_TOKEN_URL": "https://issuer.example/token",
            "OIDC_USERINFO_URL": "https://issuer.example/userinfo",
            "OIDC_CLIENT_ID": "client",
            "OIDC_CLIENT_SECRET": "secret",
            "OIDC_REDIRECT_URI": "https://app.example/callback",
            "OIDC_ISSUER": "https://issuer.example",
            "OIDC_AUDIENCE": "client",
            "OIDC_JWKS_URL": "https://issuer.example/jwks",
        }.items():
            setattr(settings, name, value)
        redis = Redis()
        try:
            result = await ExternalIdentityService.start_oidc(
                SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(redis=redis)))
            )
            query = parse_qs(urlparse(result["authorization_url"]).query)
            state = query["state"][0]
            state_payload = json.loads(redis.value[1])
            assert query["nonce"][0] == state_payload["nonce"]
            assert query["code_challenge_method"] == ["S256"]
            assert state_payload["code_verifier"]
            assert redis.value[0].endswith(state)
        finally:
            for name, value in original.items():
                setattr(settings, name, value)

    anyio.run(run)


def test_oidc_id_token_signature_and_claims_are_validated() -> None:
    async def run() -> None:
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
        jwk["kid"] = "test-key"
        token = jwt.encode(
            {
                "iss": "https://issuer.example",
                "aud": "client",
                "sub": "subject",
                "nonce": "nonce",
                "iat": datetime.now().timestamp(),
                "exp": datetime.now().timestamp() + 300,
                "email": "verified@example.com",
                "email_verified": True,
            },
            private_key,
            algorithm="RS256",
            headers={"kid": "test-key"},
        )

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {"keys": [jwk]}

        class Client:
            async def get(self, _url):
                return Response()

        original = {
            name: getattr(settings, name)
            for name in ("OIDC_ISSUER", "OIDC_AUDIENCE", "OIDC_JWKS_URL")
        }
        settings.OIDC_ISSUER = "https://issuer.example"
        settings.OIDC_AUDIENCE = "client"
        settings.OIDC_JWKS_URL = "https://issuer.example/jwks"
        try:
            claims = await ExternalIdentityService._validate_id_token(
                token, "nonce", Client()
            )
            assert claims["sub"] == "subject"
            with pytest.raises(HTTPException, match="nonce"):
                await ExternalIdentityService._validate_id_token(
                    token, "wrong", Client()
                )
        finally:
            for name, value in original.items():
                setattr(settings, name, value)

    anyio.run(run)


def test_user_list_and_excel_export_mask_fields_without_permission(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        item = {
            "id": 7,
            "email": "user@example.com",
            "phone": "13800138000",
            "avatar": "avatar.png",
        }

        class Page:
            def __init__(self, items):
                self.items = items

            def model_copy(self, update):
                return Page(update["items"])

        page = Page([item])

        async def list_users(*_args, **_kwargs):
            return page

        async def field_permission(_user_id, _resource, field_name, _request):
            return field_name == "avatar"

        monkeypatch.setattr(UserDao, "list_users", list_users)
        monkeypatch.setattr(
            "module_admin.service.user_service.PermissionDao.has_field_permission",
            field_permission,
        )
        request = _request(user_id=7)
        result = await UserService.list_users_services(
            request, None, None, None, None, None, None, Params()
        )
        assert result.items[0]["email"] is None
        assert result.items[0]["phone"] is None
        assert result.items[0]["avatar"] == "avatar.png"

        class Mysql:
            async def execute(self, _statement):
                return _Result(
                    [
                        SimpleNamespace(
                            username="user",
                            email="user@example.com",
                            phone="13800138000",
                            avatar="avatar.png",
                            nickname="User",
                            status="1",
                            dept_id=1,
                        )
                    ]
                )

        downloaded = {}
        monkeypatch.setattr(
            ExcelService,
            "_download",
            staticmethod(
                lambda filename, headers, rows: downloaded.update(
                    {"filename": filename, "headers": headers, "rows": rows}
                )
            ),
        )
        export_request = _request(user_id=7, tenant_id=1, mysql=Mysql())
        await ExcelService.export_users(export_request)
        assert downloaded["rows"][0][1:4] == [None, None, "avatar.png"]

    anyio.run(run)


def test_scheduler_executes_handler_and_releases_owned_lock() -> None:
    async def run() -> None:
        job = ScheduledJobDo(
            id=1,
            job_name="Test",
            job_key="test-job",
            task_name="test.handler",
            cron_expression="* * * * *",
            timeout_seconds=2,
            max_retries=0,
        )

        class Redis:
            def __init__(self):
                self._data = {}

            async def set(self, key, value, ex=None, nx=False):
                if nx and key in self._data:
                    return None
                self._data[key] = value
                return True

            async def get(self, key):
                return self._data.get(key)

            async def delete(self, key):
                self._data.pop(key, None)

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def get(self, _model, _job_id):
                return job

            def add(self, _item):
                return None

            async def commit(self):
                return None

        redis = Redis()
        scheduler = JobScheduler(lambda: lambda: Session(), "UTC", redis=redis)
        scheduler.register_task("test.handler", lambda _args: "ok")
        status, message = await scheduler._execute(1)
        assert (status, message) == ("success", "ok")
        assert not redis._data

    anyio.run(run)


def test_permission_queries_use_modern_user_role_binding_and_tenant() -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                return _Result()

        request = _request(mysql=Mysql(), tenant_id=11)
        assert not await PermissionDao.has_permission(7, "system:user:list", request)
        assert not await PermissionDao.has_field_permission(7, "user", "email", request)

        sql = "\n".join(str(statement) for statement in statements)
        assert "user_role.user_id" in sql
        assert "tenant_members.tenant_id" in sql
        assert "roles.tenant_id" in sql

    anyio.run(run)


def test_refresh_memory_cache_is_bounded() -> None:
    async def run() -> None:
        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace(redis=None)),
            state=SimpleNamespace(),
        )
        original_limit = Auth.MAX_MEMORY_REFRESH_CACHE_SIZE
        Auth.MAX_MEMORY_REFRESH_CACHE_SIZE = 2
        Auth._refresh_cache.clear()
        try:
            for user_id in range(3):
                await Auth.create_refresh_token({"user_id": user_id}, request)
            assert len(Auth._refresh_cache) == 2
        finally:
            Auth.MAX_MEMORY_REFRESH_CACHE_SIZE = original_limit
            Auth._refresh_cache.clear()

    anyio.run(run)


def test_scheduler_lock_is_deleted_only_by_owner() -> None:
    async def run() -> None:
        class Redis:
            def __init__(self):
                self._data = {"job-lock": "owner"}
                self.value = "owner"

            async def get(self, _key):
                return self._data.get(_key)

            async def delete(self, key):
                self._data.pop(key, None)
                self.value = None

        redis = Redis()
        scheduler = JobScheduler(lambda: None, "UTC", redis=redis)
        await scheduler._release_lock("job-lock", "other")
        assert redis.value == "owner"
        await scheduler._release_lock("job-lock", "owner")
        assert redis.value is None

    anyio.run(run)


def test_system_config_secret_values_are_encrypted_and_masked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        captured = {}
        item = SystemConfigDo(
            id=1,
            config_name="Webhook",
            config_key="webhook.secret",
            config_value=None,
            config_type="secret",
        )

        async def missing(*_args, **_kwargs):
            return None

        async def create(data, _request):
            captured["data"] = data
            item.config_value = data.config_value
            return item

        monkeypatch.setattr(SystemConfigDao, "get_by_key", missing)
        monkeypatch.setattr(SystemConfigDao, "create", create)
        request = _request(tenant_id=11)
        data = SystemConfigCreateDto(
            config_name="Webhook",
            config_key="webhook.secret",
            config_value="real-secret",
            config_type="secret",
        )

        result = await SystemConfigService.create(data, request)
        assert captured["data"].config_value != "real-secret"
        assert str(captured["data"].config_value).startswith("enc:v1:")
        assert result.config_value == SystemConfigService.MASKED_VALUE

        async def get_item(*_args, **_kwargs):
            return item

        monkeypatch.setattr(SystemConfigDao, "get_by_key", get_item)
        value = await SystemConfigService.value("webhook.secret", request)
        assert value["config_value"] == SystemConfigService.MASKED_VALUE

    anyio.run(run)


def test_system_config_standard_crud_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> None:
        captured = {}
        item = SystemConfigDo(
            id=2,
            config_name="Name",
            config_key="app.name",
            config_value="value",
            config_type="text",
            is_builtin=False,
        )

        class Page:
            items = [item]

            def model_copy(self, update):
                page = Page()
                page.items = update["items"]
                return page

        async def list_configs(*_args, **_kwargs):
            return Page()

        async def get_by_id(*_args, **_kwargs):
            return item

        async def update(*_args, **_kwargs):
            captured["update_data"] = _args[1]
            return item

        async def delete(*_args, **_kwargs):
            return item

        monkeypatch.setattr(SystemConfigDao, "list_configs", list_configs)
        monkeypatch.setattr(SystemConfigDao, "get_by_id", get_by_id)
        monkeypatch.setattr(SystemConfigDao, "update", update)
        monkeypatch.setattr(SystemConfigDao, "delete", delete)
        request = _request()
        page = await SystemConfigService.list_configs(request, None, None, Params())
        assert page.items[0].config_value == "value"
        assert (await SystemConfigService.detail(2, request)).config_value == "value"
        await SystemConfigService.update(
            2,
            SystemConfigUpdateDto(config_value="next"),
            request,
        )
        await SystemConfigService.update(
            2,
            SystemConfigUpdateDto(config_type="secret"),
            request,
        )
        assert str(captured["update_data"].config_value).startswith("enc:v1:")
        item.config_type = "secret"
        item.config_value = captured["update_data"].config_value
        await SystemConfigService.update(
            2,
            SystemConfigUpdateDto(config_value=SystemConfigService.MASKED_VALUE),
            request,
        )
        assert captured["update_data"].config_value == item.config_value
        await SystemConfigService.delete(2, request)

    anyio.run(run)


def test_external_login_verifies_mfa_before_token_creation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        user = SimpleNamespace(
            id=7,
            status="1",
            auth_provider="local",
            auth_subject=None,
            tenant_id=1,
        )
        calls = []

        async def find_subject(*_args, **_kwargs):
            return None

        async def find_identifier(*_args, **_kwargs):
            return user

        async def verify_mfa(actual_user, code, *_args):
            calls.append((actual_user, code))

        async def token_response(actual_user, _request):
            return {"user_id": actual_user.id}

        async def active_tenant(*_args, **_kwargs):
            return user

        monkeypatch.setattr(UserDao, "get_user_by_external_subject", find_subject)
        monkeypatch.setattr(UserDao, "get_user_by_identifier", find_identifier)
        monkeypatch.setattr(TenantDao, "get", active_tenant)
        monkeypatch.setattr(MfaService, "verify_login", verify_mfa)
        monkeypatch.setattr(
            "module_admin.service.external_identity_service.UserService._create_token_response",
            token_response,
        )

        result = await ExternalIdentityService._login_external_user(
            "oidc",
            "subject",
            {"email": "verified@example.com"},
            _request(tenant_id=1),
            mfa_code="123456",
            allow_email_link=True,
        )
        assert result == {"user_id": 7}
        assert calls == [(user, "123456")]

    anyio.run(run)


def test_chunk_init_and_upload_write_tenant_owned_files(tmp_path: Path) -> None:
    async def run() -> None:
        class Mysql:
            def __init__(self):
                self.added = []
                self.item = FileChunkUploadDo(
                    upload_id="12345678-1234-5678-1234-567812345678",
                    tenant_id=1,
                    created_by=7,
                    original_name="file.txt",
                    total_size=3,
                    total_chunks=1,
                )

            def add(self, item):
                self.added.append(item)

            async def get(self, _model, _upload_id):
                return self.item

        class Upload:
            def __init__(self):
                self.chunks = [b"abc", b""]

            async def read(self, _size):
                return self.chunks.pop(0)

        app_settings = SimpleNamespace(
            FILE_UPLOAD_DIR=str(tmp_path),
            FILE_ALLOWED_EXTENSIONS=[".txt"],
            FILE_MAX_SIZE_BYTES=100,
        )
        mysql = Mysql()
        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace(settings=app_settings)),
            state=SimpleNamespace(mysql=mysql, tenant_id=1, user_id=7),
        )
        init_result = await FileService.init_chunk_upload(
            SimpleNamespace(
                filename="file.txt",
                content_type="text/plain",
                total_size=3,
                total_chunks=1,
            ),
            request,
        )
        assert init_result["total_chunks"] == 1
        upload_id = mysql.added[0].upload_id
        result = await FileService.upload_chunk(upload_id, 0, Upload(), request)
        assert result["received"] == 1
        assert (tmp_path / ".chunks" / upload_id / "0.part").read_bytes() == b"abc"

    anyio.run(run)


def test_expired_chunk_cleanup_removes_database_rows_and_directories(
    tmp_path: Path,
) -> None:
    async def run() -> None:
        upload_id = "12345678-1234-5678-1234-567812345678"
        chunk_root = tmp_path / ".chunks"
        (chunk_root / upload_id).mkdir(parents=True)
        (chunk_root / upload_id / "0.part").write_bytes(b"chunk")
        item = FileChunkUploadDo(
            upload_id=upload_id,
            original_name="file.txt",
            total_size=5,
            total_chunks=1,
            updated_at=datetime.now() - timedelta(days=2),
        )

        class Session:
            def __init__(self):
                self.deleted = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, _statement):
                return _Result([item])

            async def delete(self, deleted):
                self.deleted.append(deleted)

            async def commit(self):
                return None

        session = Session()
        settings = SimpleNamespace(
            FILE_UPLOAD_DIR=str(tmp_path), FILE_CHUNK_TTL_SECONDS=60
        )
        result = await FileService.cleanup_expired_chunks(
            lambda: session,
            settings,
        )
        assert result == 1
        assert session.deleted == [item]
        assert not (chunk_root / upload_id).exists()

    anyio.run(run)


def test_external_disabled_user_is_rejected_before_token() -> None:
    async def run() -> None:
        user = SimpleNamespace(
            id=7,
            status="0",
            auth_provider="oidc",
            auth_subject="subject",
            tenant_id=1,
        )

        async def find_subject(*_args, **_kwargs):
            return user

        async def active_tenant(*_args, **_kwargs):
            return user

        request = _request(tenant_id=1)
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(UserDao, "get_user_by_external_subject", find_subject)
        monkeypatch.setattr(TenantDao, "get", active_tenant)
        try:
            with pytest.raises(HTTPException) as exception:
                await ExternalIdentityService._login_external_user(
                    "oidc", "subject", {}, request
                )
            assert exception.value.status_code == 403
        finally:
            monkeypatch.undo()

    anyio.run(run)


def test_idempotency_authenticates_before_claim_and_skips_auth_routes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        order = []

        class SessionContext:
            async def __aenter__(self):
                return object()

            async def __aexit__(self, *_args):
                return False

        class SessionFactory:
            def __call__(self):
                return SessionContext()

        async def authenticate(request, _authorization):
            order.append("auth")
            request.state.user_id = 1
            request.state.tenant_id = 1

        async def claim(_request, _key, _request_hash):
            order.append("claim")
            return None

        async def complete(*_args):
            order.append("complete")

        async def release(*_args):
            order.append("release")

        monkeypatch.setattr(Auth, "router_auth", authenticate)
        monkeypatch.setattr(IdempotencyService, "claim", claim)
        monkeypatch.setattr(IdempotencyService, "complete", complete)
        monkeypatch.setattr(IdempotencyService, "release", release)

        app = SimpleNamespace(state=SimpleNamespace(mysql_session_factory=SessionFactory()))

        async def receive():
            return {"type": "http.request", "body": b"{}", "more_body": False}

        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/user/add",
                "query_string": b"",
                "headers": [(b"authorization", b"Bearer active"), (b"idempotency-key", b"k")],
                "app": app,
            },
            receive,
        )

        async def call_next(_request):
            order.append("route")

            async def body():
                yield b'{"ok":true}'

            return StreamingResponse(body(), media_type="application/json")

        response = await IdempotencyMiddleware.dispatch(
            object.__new__(IdempotencyMiddleware), request, call_next
        )
        assert response.status_code == 200
        assert order == ["auth", "claim", "route", "complete"]

        auth_route_request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/user/logout",
                "query_string": b"",
                "headers": [(b"authorization", b"Bearer active"), (b"idempotency-key", b"k")],
                "app": app,
            },
            receive,
        )
        order.clear()
        await IdempotencyMiddleware.dispatch(
            object.__new__(IdempotencyMiddleware), auth_route_request, call_next
        )
        assert order == ["route"]

    anyio.run(run)


def test_idempotency_does_not_cache_forbidden_responses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        released = False

        class SessionContext:
            async def __aenter__(self):
                return object()

            async def __aexit__(self, *_args):
                return False

        app = SimpleNamespace(
            state=SimpleNamespace(
                mysql_session_factory=lambda: SessionContext(),
            )
        )

        async def authenticate(request, _authorization):
            request.state.user_id = 1
            request.state.tenant_id = 1

        async def claim(_request, _key, _request_hash):
            return None

        async def complete(*_args):
            raise AssertionError("non-success responses must not be cached")

        async def release(*_args):
            nonlocal released
            released = True

        monkeypatch.setattr(Auth, "router_auth", authenticate)
        monkeypatch.setattr(IdempotencyService, "claim", claim)
        monkeypatch.setattr(IdempotencyService, "complete", complete)
        monkeypatch.setattr(IdempotencyService, "release", release)

        async def receive():
            return {"type": "http.request", "body": b"{}", "more_body": False}

        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/user/add",
                "query_string": b"",
                "headers": [(b"authorization", b"Bearer active"), (b"idempotency-key", b"k")],
                "app": app,
            },
            receive,
        )

        async def call_next(_request):
            return JSONResponse({"detail": "forbidden"}, status_code=403)

        response = await IdempotencyMiddleware.dispatch(
            object.__new__(IdempotencyMiddleware), request, call_next
        )
        assert response.status_code == 403
        assert released

    anyio.run(run)


def test_online_backup_restore_requires_controlled_window_and_mfa() -> None:
    async def run() -> None:
        data = BackupRestoreRequestDto(filename="backup.sql.enc", mfa_code="123456")
        app_settings = SimpleNamespace(
            BACKUP_ONLINE_RESTORE_ENABLED=False,
            BACKUP_RESTORE_MAINTENANCE_MODE=False,
            BACKUP_RESTORE_OPERATIONS_TOKEN="operations-token",
        )

        class Session:
            async def get(self, _model, _user_id):
                return SimpleNamespace(mfa_enabled=False)

        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace(settings=app_settings)),
            state=SimpleNamespace(mysql=Session(), user_id=1),
        )
        with pytest.raises(HTTPException) as disabled:
            await BackupController._controlled_restore_access(
                request, data, "operations-token"
            )
        assert disabled.value.status_code == 503

        app_settings.BACKUP_ONLINE_RESTORE_ENABLED = True
        app_settings.BACKUP_RESTORE_MAINTENANCE_MODE = True
        with pytest.raises(HTTPException) as no_mfa:
            await BackupController._controlled_restore_access(
                request, data, "operations-token"
            )
        assert no_mfa.value.status_code == 403

        restore_route = next(
            route for route in BackupController.backup.routes if route.path.endswith("/restore")
        )
        assert any(
            dependency.call is Auth.platform_admin_status
            for dependency in restore_route.dependant.dependencies
        )

    anyio.run(run)
