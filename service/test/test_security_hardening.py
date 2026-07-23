"""本次安全和一致性缺陷的最小回归测试。"""

import asyncio
import importlib
import json
import os
from datetime import datetime
from pathlib import Path
from test.unit_support import InMemoryRedis
from types import SimpleNamespace

import anyio
import pytest
from fastapi import HTTPException, Response
from sqlalchemy import select

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.dao.menu_dao import MenuDao
from module_admin.dao.tenant_dao import TenantDao
from module_admin.dao.tenant_scope import tenant_clause
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.api_permission_do import ApiPermissionCatalogDo
from module_admin.entity.do.menu_do import MenuDo
from module_admin.entity.do.permission_do import PermissionDo
from module_admin.entity.do.role_do import RoleDo
from module_admin.entity.do.user_do import UserDo
from module_admin.service.external_identity_service import \
    ExternalIdentityService
from module_admin.service.file_service import FileService
from module_admin.service.mfa_service import MfaService
from module_admin.service.notification_service import NotificationService
from module_admin.service.permission_sync_service import PermissionSyncService


class Result:
    def __init__(self, values=None, rowcount: int = 0):
        self.values = list(values or [])
        self.rowcount = rowcount

    def scalars(self):
        return self

    def all(self):
        return self.values

    def first(self):
        return self.values[0] if self.values else None


def _request(**state_values):
    return SimpleNamespace(state=SimpleNamespace(**state_values))


def test_tenant_filters_require_active_tenant() -> None:
    user_statement = select(UserDo).where(tenant_clause(_request(tenant_id=9), UserDo))
    resource_statement = select(RoleDo).where(
        tenant_clause(_request(tenant_id=9), RoleDo)
    )
    assert "tenants.status" in str(user_statement)
    assert "tenants.deleted_at" in str(user_statement)
    assert "tenants.status" in str(resource_statement)


def test_tenant_dao_get_rejects_disabled_tenants() -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            def add_all(self, _items):
                return None

            async def execute(self, statement):
                statements.append(statement)
                return Result()

        tenant = await TenantDao.get(9, _request(mysql=Mysql()))

        assert tenant is None
        assert "tenants.status" in str(statements[0])

    anyio.run(run)


def test_auth_tenant_member_query_checks_tenant_lifecycle() -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                return Result()

        member = await Auth._get_tenant_member(
            _request(mysql=Mysql()), 7, 9
        )

        assert member is None
        sql = str(statements[0])
        assert "tenants.status" in sql
        assert "tenants.deleted_at" in sql

    anyio.run(run)


def test_password_reset_consumption_is_conditional() -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                return Result(rowcount=0)

        consumed = await UserDao.consume_password_reset_token(
            "hash",
            9,
            datetime.now(),
            _request(mysql=Mysql()),
        )

        assert consumed is False
        assert "consumed_at IS NULL" in str(statements[0])

    anyio.run(run)


def test_mfa_recovery_consumption_uses_versioned_update() -> None:
    async def run() -> None:
        recovery_code = "RECOVERY-CODE"
        encrypted_codes = MfaService._encrypt(
            json.dumps([MfaService._hash_recovery_code(recovery_code)])
        )
        user = SimpleNamespace(
            id=7,
            version=4,
            mfa_enabled=True,
            mfa_secret_encrypted=MfaService._encrypt("JBSWY3DPEHPK3PXP"),
            mfa_recovery_codes_encrypted=encrypted_codes,
        )
        statements = []

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                return Result(rowcount=0)

        with pytest.raises(HTTPException, match="已使用"):
            await MfaService.verify_login(
                user,
                recovery_code,
                _request(mysql=Mysql()),
            )
        assert "mfa_recovery_codes_encrypted" in str(statements[0])
        assert "users.version" in str(statements[0])

    anyio.run(run)


def test_user_role_replacement_is_tenant_scoped() -> None:
    async def run() -> None:
        statements = []
        user = UserDo(id=7, username="user", password="password", tenant_id=9)

        class Mysql:
            def add_all(self, _items):
                return None

            async def execute(self, statement):
                statements.append(statement)
                return Result(rowcount=1)

        async def get_user(*_args, **_kwargs):
            return user

        original = UserDao.get_user_by_id
        UserDao.get_user_by_id = get_user
        try:
            result = await UserDao.bind_user_roles(
                7,
                [],
                _request(mysql=Mysql(), tenant_id=9),
            )
        finally:
            UserDao.get_user_by_id = original

        assert result is None
        assert "user_role.tenant_id" in str(statements[0])

    anyio.run(run)


def test_oidc_state_is_atomic_and_requires_browser_binding() -> None:
    async def run() -> None:
        redis = InMemoryRedis()
        state_key = f"{ExternalIdentityService.STATE_PREFIX}state"
        await redis.set(
            state_key,
            json.dumps(
                {
                    "nonce": "nonce",
                    "code_verifier": "verifier",
                    "browser_binding": "binding",
                }
            ),
        )
        values = await asyncio.gather(
            ExternalIdentityService._consume_state(redis, state_key),
            ExternalIdentityService._consume_state(redis, state_key),
        )
        assert sum(value is not None for value in values) == 1

        await redis.set(
            state_key,
            json.dumps(
                {
                    "nonce": "nonce",
                    "code_verifier": "verifier",
                    "browser_binding": "binding",
                }
            ),
        )
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            ExternalIdentityService, "_ensure_oidc_configured", lambda: None
        )
        try:
            with pytest.raises(HTTPException, match="浏览器会话"):
                await ExternalIdentityService.callback_oidc(
                    "code",
                    "state",
                    SimpleNamespace(
                        app=SimpleNamespace(state=SimpleNamespace(redis=redis)),
                        cookies={},
                    ),
                )
        finally:
            monkeypatch.undo()

    anyio.run(run)


def test_oidc_start_sets_http_only_binding_cookie(monkeypatch) -> None:
    async def run() -> None:
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
        for name in names:
            monkeypatch.setattr(
                settings,
                name,
                {
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
                }[name],
            )
        response = Response()
        await ExternalIdentityService.start_oidc(
            SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(redis=InMemoryRedis()))),
            response,
        )
        cookie = response.headers["set-cookie"]
        assert ExternalIdentityService.STATE_COOKIE_NAME in cookie
        assert "HttpOnly" in cookie

    anyio.run(run)


def test_ldap_service_account_search_escapes_filter_and_rebinds_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        import ldap3

        calls = []
        user_dn = "uid=alice,dc=example,dc=org"

        class Entry:
            entry_dn = user_dn
            uid = SimpleNamespace(value="alice")
            mail = SimpleNamespace(value="alice@example.org")
            displayName = SimpleNamespace(value="Alice")

        class Server:
            def __init__(self, *args, **kwargs):
                pass

        class Connection:
            def __init__(self, _server, user, password, auto_bind, raise_exceptions):
                calls.append((user, password, auto_bind, raise_exceptions))
                self.user = user
                self.bound = password != "wrong-password"
                self.entries = []

            def search(self, _base, search_filter, attributes):
                calls.append((search_filter, tuple(attributes)))
                self.entries = [Entry()]

            def unbind(self):
                return None

        monkeypatch.setattr(ldap3, "Server", Server)
        monkeypatch.setattr(ldap3, "Connection", Connection)
        monkeypatch.setattr(ldap3, "ALL", object())
        monkeypatch.setattr(settings, "LDAP_ENABLED", True)
        monkeypatch.setattr(settings, "LDAP_SERVER_URL", "ldap://example.org")
        monkeypatch.setattr(settings, "LDAP_BASE_DN", "dc=example,dc=org")
        monkeypatch.setattr(settings, "LDAP_BIND_DN", "cn=service")
        monkeypatch.setattr(settings, "LDAP_BIND_PASSWORD", "service-password")
        monkeypatch.setattr(settings, "LDAP_USER_FILTER", "(uid={username})")

        claims = {}
        link_options = {}

        async def login_external(*args, **kwargs):
            claims.update(args[2])
            link_options.update(kwargs)
            return claims

        monkeypatch.setattr(ExternalIdentityService, "_login_external_user", login_external)
        result = await ExternalIdentityService.login_ldap(
            "alice*)(uid=*)",
            "user-password",
            _request(),
        )

        assert result["sub"] == "alice"
        assert calls[0][0] == "cn=service"
        assert calls[0][3] is True
        assert calls[2][0] == user_dn
        assert calls[2][1] == "user-password"
        assert calls[2][3] is True
        assert "\\2a" in calls[1][0]
        assert "*)(uid=*)" not in calls[1][0]
        assert link_options["allow_email_link"] is False

        with pytest.raises(HTTPException) as error:
            await ExternalIdentityService.login_ldap(
                "alice",
                "wrong-password",
                _request(),
            )
        assert error.value.status_code == 401

    anyio.run(run)


def test_ldap_does_not_link_existing_local_account_by_email(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        local_user = SimpleNamespace(
            id=7,
            status="1",
            auth_provider="local",
            auth_subject=None,
            tenant_id=1,
        )

        async def active_tenant(*_args, **_kwargs):
            return SimpleNamespace(id=1)

        async def no_external_subject(*_args, **_kwargs):
            return None

        async def local_user_by_email(*_args, **_kwargs):
            return local_user

        monkeypatch.setattr(TenantDao, "get", active_tenant)
        monkeypatch.setattr(
            UserDao, "get_user_by_external_subject", no_external_subject
        )
        monkeypatch.setattr(UserDao, "get_user_by_identifier", local_user_by_email)

        with pytest.raises(HTTPException, match="LDAP 外部身份尚未绑定"):
            await ExternalIdentityService._login_external_user(
                "ldap",
                "directory-user",
                {"email": "local@example.com"},
                _request(tenant_id=1),
                allow_email_link=False,
            )

        assert local_user.auth_provider == "local"
        assert local_user.auth_subject is None

    anyio.run(run)


def test_permission_sync_deactivates_missing_routes() -> None:
    async def run() -> None:
        stale = ApiPermissionCatalogDo(
            id=1,
            permission_code="system:old:view",
            api_path="/api/v1/old",
            api_method="GET",
        )

        class Session:
            def __init__(self):
                self.added = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, _statement):
                return Result([stale])

            def add(self, item):
                self.added.append(item)

            async def commit(self):
                return None

        session = Session()
        count = await PermissionSyncService.sync(
            SimpleNamespace(routes=[]), lambda: session
        )

        assert count == 0
        assert stale.status == "0"

    anyio.run(run)


def test_menu_status_does_not_mutate_global_permission_status() -> None:
    async def run() -> None:
        permission = PermissionDo(
            id=1,
            code="system:tenant:edit",
            name="old",
            status="0",
        )
        menu = MenuDo(
            menu_id=1,
            menu_name="Tenant edit",
            menu_type="F",
            perms="system:tenant:edit",
            status="1",
            tenant_id=9,
        )

        class Mysql:
            async def execute(self, _statement):
                return Result([permission])

        await MenuDao._upsert_button_permission(Mysql(), menu)

        assert permission.status == "0"
        assert permission.name == "Tenant edit"

    anyio.run(run)


def test_notification_claim_cancels_pending_and_sending_for_removed_members() -> None:
    async def run() -> None:
        statements = []

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, statement):
                statements.append(statement)
                return Result()

            async def commit(self):
                return None

        delivered = await NotificationService.deliver_pending(
            lambda: Session(), settings, limit=1
        )

        assert delivered == 0
        assert 'notification_deliveries.status IN (__[POSTCOMPILE_status_1])' in str(
            statements[0]
        )

    anyio.run(run)


def test_chunk_pending_manifest_cleanup_removes_uncommitted_object(
    tmp_path: Path,
) -> None:
    async def run() -> None:
        app_settings = SimpleNamespace(
            FILE_UPLOAD_DIR=str(tmp_path),
            FILE_CHUNK_TTL_SECONDS=60,
        )
        upload_id = "12345678-1234-5678-1234-567812345678"
        storage_key = "uploads/pending.txt"
        storage_path = tmp_path / storage_key
        storage_path.parent.mkdir(parents=True)
        storage_path.write_bytes(b"orphan")
        FileService._write_pending_manifest(
            upload_id, storage_key, "local", app_settings
        )
        manifest = FileService._pending_manifest_path(upload_id, app_settings)
        old = datetime.now().timestamp() - 120
        os.utime(manifest, (old, old))

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, _statement):
                return Result()

        removed = await FileService.cleanup_expired_chunks(
            lambda: Session(), app_settings
        )

        assert removed == 1
        assert not manifest.exists()
        assert not storage_path.exists()

    anyio.run(run)


def test_0024_downgrade_refuses_permission_data_loss(monkeypatch) -> None:
    async def run() -> None:
        migration_path = (
            Path(__file__).parents[1]
            / "alembic"
            / "versions"
            / "0024_password_reset_tenant_permissions.py"
        )
        spec = importlib.util.spec_from_file_location("migration_0024", migration_path)
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)

        class Bind:
            def execute(self, _statement):
                return Result([("/api/v1/user", "PUT")])

        monkeypatch.setattr(migration.op, "get_bind", lambda: Bind())
        with pytest.raises(RuntimeError, match="权限目录"):
            migration.downgrade()

    anyio.run(run)
