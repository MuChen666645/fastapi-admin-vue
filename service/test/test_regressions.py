"""针对租户、权限目录、存储补偿和任务锁的回归测试。"""

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import anyio
import pytest
from fastapi import Depends, FastAPI, HTTPException

from config.env import settings
from config.mysql_serve import bind_request_mysql_session
from module_admin.auth.authorization import Auth
from module_admin.dao.tenant_dao import TenantDao
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.export_do import ExportTaskDo
from module_admin.entity.do.file_do import FileMetadataDo
from module_admin.entity.do.notice_do import NoticeDo
from module_admin.entity.do.notification_do import NotificationDeliveryDo
from module_admin.entity.do.tenant_do import TenantMemberDo
from module_admin.entity.do.user_do import PasswordResetTokenDo, UserDo
from module_admin.entity.dto.user_dto import (
    ConfirmPasswordResetRequestDto,
    ForgotPasswordRequestDto,
)
from module_admin.service.excel_service import ExcelService
from module_admin.service.export_service import ExportService, ExportTaskRef
from module_admin.service.external_identity_service import ExternalIdentityService
from module_admin.service.job_scheduler import JobScheduler
from module_admin.service.mfa_service import MfaService
from module_admin.service.notification_service import NotificationService
from module_admin.service.password_reset_service import (
    PasswordResetNotifier,
    PasswordResetService,
)
from module_admin.service.permission_sync_service import PermissionSyncService
from module_admin.service.user_service import UserService


class Result:
    def __init__(self, values=None):
        self.values = list(values or [])

    def scalars(self):
        return self

    def all(self):
        return self.values

    def first(self):
        return self.values[0] if self.values else None


def test_password_reset_requires_tenant_and_uses_member_scope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        user = UserDo(
            id=7,
            username="reset-user",
            password="old-password",
            email="reset@example.com",
            tenant_id=1,
        )
        captured = {}

        async def find(identifier, _request, tenant_id=None):
            captured["lookup"] = (identifier, tenant_id)
            return user

        class Mysql:
            def __init__(self):
                self.added = []

            async def execute(self, statement):
                captured.setdefault("statements", []).append(statement)
                return Result()

            def add(self, item):
                self.added.append(item)

        class Notifier:
            async def send(self, channel, destination, token):
                captured["notification"] = (channel, destination, token)

        mysql = Mysql()
        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(password_reset_notifier=Notifier())
            ),
            state=SimpleNamespace(mysql=mysql),
        )
        monkeypatch.setattr(UserDao, "get_user_by_identifier", find)

        data = ForgotPasswordRequestDto(
            tenant_id=9,
            identifier="reset@example.com",
            channel="email",
        )
        result = await PasswordResetService.request_reset(data, request)

        assert result["message"]
        assert captured["lookup"] == ("reset@example.com", 9)
        token = mysql.added[0]
        assert isinstance(token, PasswordResetTokenDo)
        assert token.tenant_id == 9
        assert "tenant_members" not in str(captured["statements"][0])

        with pytest.raises(Exception):
            ForgotPasswordRequestDto(identifier="reset@example.com")

    anyio.run(run)


def test_password_reset_invalid_token_is_rejected_for_requested_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        async def consume(*_args, **_kwargs):
            return False

        monkeypatch.setattr(UserDao, "consume_password_reset_token", consume)
        request = SimpleNamespace(state=SimpleNamespace(mysql=object()))
        data = ConfirmPasswordResetRequestDto(
            tenant_id=9, token="x" * 48, password="New-Password1!"
        )

        with pytest.raises(HTTPException) as exc_info:
            await PasswordResetService.confirm_reset(data, request)
        assert exc_info.value.status_code == 400

    anyio.run(run)


def test_password_reset_notifier_handles_development_and_invalid_smtp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        notifier = PasswordResetNotifier()
        monkeypatch.setattr(settings, "PASSWORD_RESET_SMS_WEBHOOK", "")
        await notifier.send("sms", "13900000000", "sms-token")

        monkeypatch.setattr(settings, "PASSWORD_RESET_EMAIL_ENABLED", False)
        await notifier.send("email", "user@example.com", "email-token")

        monkeypatch.setattr(settings, "PASSWORD_RESET_EMAIL_ENABLED", True)
        monkeypatch.setattr(settings, "SMTP_HOST", "")
        with pytest.raises(RuntimeError, match="SMTP"):
            await notifier.send("email", "user@example.com", "email-token")

    anyio.run(run)


def test_password_reset_request_keeps_account_enumeration_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        data = ForgotPasswordRequestDto(tenant_id=9, identifier="missing@example.com")
        request = SimpleNamespace(
            app=SimpleNamespace(state=SimpleNamespace()),
            state=SimpleNamespace(mysql=SimpleNamespace()),
        )

        async def missing(*_args, **_kwargs):
            return None

        monkeypatch.setattr(UserDao, "get_user_by_identifier", missing)
        result = await PasswordResetService.request_reset(data, request)
        assert "如果账号存在" in result["message"]

        user = UserDo(
            id=7,
            username="no-email",
            password="password",
            email=None,
            phone=None,
            tenant_id=1,
        )

        async def found(*_args, **_kwargs):
            return user

        monkeypatch.setattr(UserDao, "get_user_by_identifier", found)
        result = await PasswordResetService.request_reset(data, request)
        assert "如果账号存在" in result["message"]

    anyio.run(run)


def test_password_reset_confirm_updates_password_and_consumes_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        data = ConfirmPasswordResetRequestDto(
            tenant_id=9, token="x" * 48, password="New-Password1!"
        )
        reset = PasswordResetTokenDo(
            id=1,
            tenant_id=9,
            user_id=7,
            channel="email",
            token_hash="hash",
            expires_at=datetime.now() + timedelta(minutes=5),
        )
        user = UserDo(
            id=7,
            username="reset-user",
            password="old-password",
            tenant_id=1,
        )

        class Mysql:
            def __init__(self):
                self.added = []
                self.calls = 0

            async def execute(self, _statement):
                self.calls += 1
                return Result([reset] if self.calls == 1 else [user])

            def add(self, item):
                self.added.append(item)

        async def validate(*_args, **_kwargs):
            return None

        async def update(*_args, **_kwargs):
            return None

        async def record(*_args, **_kwargs):
            return None

        async def revoke(*_args, **_kwargs):
            return None

        async def consume(*_args, **_kwargs):
            return True

        monkeypatch.setattr(UserDao, "consume_password_reset_token", consume)
        monkeypatch.setattr(UserService, "_validate_new_password", validate)
        monkeypatch.setattr(UserDao, "update_password_without_scope", update)
        monkeypatch.setattr(UserService, "_record_login", record)
        monkeypatch.setattr(Auth, "revoke_all_user_tokens", revoke)
        request = SimpleNamespace(state=SimpleNamespace(mysql=Mysql()))

        result = await PasswordResetService.confirm_reset(data, request)

        assert result["message"] == "密码已重置，请重新登录"
        assert reset.consumed_at is not None

    anyio.run(run)


def test_user_identifier_query_uses_tenant_membership() -> None:
    async def run() -> None:
        statements = []

        class Mysql:
            async def execute(self, statement):
                statements.append(statement)
                return Result()

        request = SimpleNamespace(state=SimpleNamespace(mysql=Mysql()))
        await UserDao.get_user_by_identifier("user@example.com", request, tenant_id=9)

        assert "tenant_members" in str(statements[0])
        assert "users.tenant_id =" not in str(statements[0])

    anyio.run(run)


def test_permission_sync_keeps_all_permissions_for_one_route() -> None:
    async def run() -> None:
        application = FastAPI()

        @application.post(
            "/users/{user_id}/roles",
            dependencies=[
                Depends(Auth.has_permission("system:user:edit")),
                Depends(Auth.has_permission("system:role:edit")),
            ],
        )
        async def bind_roles(user_id: int):
            return {"user_id": user_id}

        class Session:
            def __init__(self):
                self.added = []

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, _statement):
                return Result()

            def add(self, item):
                self.added.append(item)

            async def commit(self):
                return None

        session = Session()
        count = await PermissionSyncService.sync(application, lambda: session)

        assert count == 2
        assert {item.permission_code for item in session.added} == {
            "system:user:edit",
            "system:role:edit",
        }

    anyio.run(run)


def test_notification_enqueue_uses_membership_not_primary_tenant() -> None:
    async def run() -> None:
        user = UserDo(
            id=3,
            username="tenant-member",
            password="password",
            email="member@example.com",
            tenant_id=1,
        )
        notice = NoticeDo(
            id=5,
            tenant_id=9,
            notice_title="Tenant notice",
            notice_content="Content",
        )

        class Mysql:
            def __init__(self):
                self.calls = 0
                self.added = []
                self.statements = []

            async def execute(self, statement):
                self.calls += 1
                self.statements.append(statement)
                return Result([user.id] if self.calls == 1 else [user])

            def add(self, item):
                self.added.append(item)

        mysql = Mysql()
        request = SimpleNamespace(state=SimpleNamespace(mysql=mysql))
        data = SimpleNamespace(recipient_user_ids=[], delivery_channels=["inbox"])

        count = await NotificationService.enqueue(notice, data, request)

        assert count == 1
        assert mysql.added[0].tenant_id == 9
        sql = "\n".join(str(statement) for statement in mysql.statements)
        assert "tenant_members" in sql

    anyio.run(run)


def test_notification_delivery_ignores_removed_tenant_members(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        item = NotificationDeliveryDo(
            id=1,
            tenant_id=9,
            notice_id=5,
            user_id=3,
            channel="webhook",
            status="sending",
            lease_token="lease",
        )

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def execute(self, _statement):
                return Result([])

            async def get(self, _model, _item_id):
                return item

            async def commit(self):
                return None

        delivered = await NotificationService._deliver_claim(
            1,
            "lease",
            lambda: Session(),
            settings,
        )

        assert delivered == 0
        assert item.status == "cancelled"

    anyio.run(run)


def test_request_database_rollback_removes_uploaded_object(tmp_path: Path) -> None:
    async def run() -> None:
        app_settings = settings.model_copy(
            update={"FILE_STORAGE_BACKEND": "local", "FILE_UPLOAD_DIR": str(tmp_path)}
        )
        storage_key = "uploads/rollback.txt"
        stored_path = tmp_path / storage_key
        stored_path.parent.mkdir(parents=True)
        stored_path.write_bytes(b"orphan")
        metadata = FileMetadataDo(
            file_id="12345678-1234-5678-1234-567812345678",
            tenant_id=9,
            original_name="rollback.txt",
            storage_key=storage_key,
            storage_backend="local",
            content_type="text/plain",
            file_size=6,
        )

        class Session:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def commit(self):
                raise RuntimeError("database commit failed")

            async def rollback(self):
                return None

        request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(mysql_session_factory=lambda: Session())
            ),
            state=SimpleNamespace(
                pending_storage_objects=[(metadata, app_settings)],
            ),
        )

        with pytest.raises(RuntimeError):
            async for _ in bind_request_mysql_session(request):
                pass
        assert not stored_path.exists()

    anyio.run(run)


def test_async_export_commit_failure_removes_created_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def run() -> None:
        app_settings = settings.model_copy(
            update={
                "FILE_STORAGE_BACKEND": "local",
                "FILE_UPLOAD_DIR": str(tmp_path),
                "FILE_ALLOWED_EXTENSIONS": [".xlsx"],
            }
        )
        task = ExportTaskDo(
            id="12345678-1234-5678-1234-567812345678",
            tenant_id=9,
            created_by=3,
            resource="users",
            status="running",
        )

        class Session:
            def __init__(self):
                self.commit_count = 0

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def get(self, model, _item_id):
                return task if model is ExportTaskDo else None

            def add(self, _item):
                return None

            async def commit(self):
                self.commit_count += 1
                if self.commit_count == 1:
                    raise RuntimeError("database commit failed")

            async def rollback(self):
                task.status = "running"
                task.file_id = None

        async def build_export(*_args):
            return "result.xlsx", ["column"], [["value"]]

        monkeypatch.setattr(ExcelService, "build_export", build_export)
        monkeypatch.setattr(
            ExcelService, "_workbook_bytes", staticmethod(lambda *_args: b"xlsx")
        )
        session = Session()
        await ExportService._execute(
            ExportTaskRef(task.id, task.tenant_id, task.created_by, task.resource),
            lambda: session,
            app_settings,
        )

        assert task.status == "failed"
        assert not list(tmp_path.rglob("*.xlsx"))

    anyio.run(run)


def test_scheduler_fails_closed_when_lock_adapter_rejects_nx() -> None:
    async def run() -> None:
        class BrokenRedis:
            async def set(self, *_args, **_kwargs):
                raise TypeError("nx is unsupported")

        called = False

        def session_factory():
            nonlocal called
            called = True
            return None

        scheduler = JobScheduler(session_factory, "UTC", redis=BrokenRedis())
        status, message = await scheduler._execute(7)

        assert status == "failed"
        assert "任务锁不可用" in message
        assert called is False

    anyio.run(run)


def test_scheduler_skips_when_another_instance_holds_lock() -> None:
    async def run() -> None:
        class HeldRedis:
            async def set(self, *_args, **_kwargs):
                return None

        scheduler = JobScheduler(lambda: None, "UTC", redis=HeldRedis())
        status, message = await scheduler._execute(7)

        assert (status, message) == ("skipped", "任务正在其他实例执行")

    anyio.run(run)


def test_external_login_adds_tenant_membership_for_new_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def run() -> None:
        class Mysql:
            def __init__(self):
                self.added = []

            def add(self, item):
                self.added.append(item)

            async def flush(self):
                self.added[0].id = 17

        async def no_user(*_args, **_kwargs):
            return None

        async def verify(*_args, **_kwargs):
            return None

        async def token_response(user, _request):
            return {"user_id": user.id}

        async def active_tenant(*_args, **_kwargs):
            return object()

        mysql = Mysql()
        request = SimpleNamespace(
            state=SimpleNamespace(mysql=mysql, tenant_id=9),
            app=SimpleNamespace(state=SimpleNamespace()),
        )
        monkeypatch.setattr(UserDao, "get_user_by_external_subject", no_user)
        monkeypatch.setattr(UserDao, "get_user_by_identifier", no_user)
        monkeypatch.setattr(TenantDao, "get", active_tenant)
        monkeypatch.setattr(MfaService, "verify_login", verify)
        monkeypatch.setattr(
            "module_admin.service.external_identity_service.UserService._create_token_response",
            token_response,
        )

        result = await ExternalIdentityService._login_external_user(
            "oidc", "subject-1", {"email": "new@example.com"}, request
        )

        assert result == {"user_id": 17}
        assert any(
            isinstance(item, TenantMemberDo)
            and item.user_id == 17
            and item.tenant_id == 9
            for item in mysql.added
        )

    anyio.run(run)
