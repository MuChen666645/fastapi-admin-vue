import json
from types import SimpleNamespace

import anyio
import pytest
from cryptography.fernet import Fernet
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from config.env import settings
from main import create_app
from module_admin.entity.do.export_do import ExportTaskDo
from module_admin.entity.dto.role_dto import CreateRoleDto
from module_admin.service.export_service import ExportService
from module_admin.service.secret_manager import SecretManager
from module_admin.service.task_queue import TaskQueue


class HeartbeatRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def set(self, key: str, value: str, ex: int) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


def test_create_role_dto_requires_name_and_code() -> None:
    with pytest.raises(ValidationError):
        CreateRoleDto()


def test_secret_manager_rotates_versioned_fernet_keys() -> None:
    first_key = Fernet.generate_key().decode("ascii")
    second_key = Fernet.generate_key().decode("ascii")
    configured = settings.model_copy(
        update={
            "SECRET_MANAGER_ACTIVE_VERSION": "v1",
            "SECRET_MANAGER_KEYS": json.dumps({"v1": first_key, "v2": second_key}),
        }
    )
    encrypted = SecretManager.encrypt("database-password", configured)
    rotated = SecretManager.rotate(
        encrypted,
        configured.model_copy(update={"SECRET_MANAGER_ACTIVE_VERSION": "v2"}),
    )

    assert encrypted.startswith("enc:v1:")
    assert rotated.startswith("enc:v2:")
    assert SecretManager.decrypt(rotated, configured) == "database-password"


def test_task_queue_heartbeat_is_removed_on_worker_shutdown() -> None:
    redis = HeartbeatRedis()
    queue = TaskQueue(redis, "fastapi:tasks", "fastapi-workers")

    async def run() -> None:
        await queue.heartbeat("worker-a", 15)
        assert redis.values == {"fastapi:tasks:worker:worker-a": "alive"}
        await queue.clear_heartbeat("worker-a")
        assert redis.values == {}

    anyio.run(run)


def test_async_export_task_is_persistent_and_tenant_owned() -> None:
    class Session:
        def __init__(self, task: ExportTaskDo | None = None) -> None:
            self.task = task
            self.committed = False

        def add(self, task: ExportTaskDo) -> None:
            self.task = task

        async def commit(self) -> None:
            self.committed = True

        async def get(self, model, task_id: str):
            return self.task if self.task and self.task.id == task_id else None

    session = Session()
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(settings=settings)),
        state=SimpleNamespace(mysql=session, tenant_id=7, user_id=11),
    )

    async def run() -> None:
        created = await ExportService.create("users", request)
        assert created["status"] == "pending"
        assert session.committed is True
        assert session.task is not None

        status = await ExportService.get_task(created["task_id"], request)
        assert status["resource"] == "users"

        request.state.tenant_id = 8
        with pytest.raises(HTTPException) as exc_info:
            await ExportService.get_task(created["task_id"], request)
        assert exc_info.value.status_code == 404

    anyio.run(run)


def test_production_operations_endpoints_require_dedicated_tokens() -> None:
    configured = settings.model_copy(
        update={
            "DEBUG": False,
            "DOCS_AUTH_TOKEN": "docs-token",
            "METRICS_AUTH_TOKEN": "metrics-token",
        }
    )
    application = create_app(configured)

    async def run() -> None:
        async with AsyncClient(
            transport=ASGITransport(app=application), base_url="http://testserver"
        ) as client:
            docs = await client.get("/docs")
            openapi = await client.get("/openapi.json")
            metrics = await client.get("/metrics")
            authorized_docs = await client.get(
                "/docs", headers={"X-Operations-Token": "docs-token"}
            )
            authorized_metrics = await client.get(
                "/metrics", headers={"X-Operations-Token": "metrics-token"}
            )

        assert docs.status_code == 401
        assert openapi.status_code == 401
        assert metrics.status_code == 401
        assert authorized_docs.status_code == 200
        assert authorized_metrics.status_code == 200

    anyio.run(run)
