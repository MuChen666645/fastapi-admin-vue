from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, UploadFile

from config.env import settings
from main import app
from module_admin.service.file_service import FileService


class FakeSession:
    def __init__(self) -> None:
        self.items = []

    def add(self, item) -> None:
        self.items.append(item)

    async def delete(self, item) -> None:
        self.items.remove(item)


def _request(tmp_path: Path):
    app_settings = settings.model_copy(
        update={
            "FILE_STORAGE_BACKEND": "local",
            "FILE_UPLOAD_DIR": str(tmp_path),
            "FILE_ALLOWED_EXTENSIONS": [".txt"],
            "FILE_MAX_SIZE_BYTES": 5,
        }
    )
    session = FakeSession()
    return (
        SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(settings=app_settings),
            ),
            state=SimpleNamespace(mysql=session, user_id=7),
        ),
        session,
    )


def test_local_file_upload_and_delete_are_safe(tmp_path: Path) -> None:
    request, session = _request(tmp_path)
    upload = UploadFile(filename="report.txt", file=BytesIO(b"hello"))

    async def run() -> None:
        metadata = await FileService.upload(upload, request)

        assert metadata.file_size == 5
        assert metadata.created_by == 7
        assert len(session.items) == 1
        stored_path = tmp_path / metadata.storage_key
        assert stored_path.read_bytes() == b"hello"

        await FileService.delete(metadata, request)
        assert not stored_path.exists()

    import asyncio

    asyncio.run(run())


def test_local_file_upload_rejects_extension_and_size(tmp_path: Path) -> None:
    request, _ = _request(tmp_path)

    async def run() -> None:
        with pytest.raises(HTTPException) as extension_error:
            await FileService.upload(
                UploadFile(filename="report.exe", file=BytesIO(b"hello")),
                request,
            )
        assert extension_error.value.status_code == 400

        with pytest.raises(HTTPException) as size_error:
            await FileService.upload(
                UploadFile(filename="report.txt", file=BytesIO(b"too large")),
                request,
            )
        assert size_error.value.status_code == 413

    import asyncio

    asyncio.run(run())


def test_admin_operation_routes_are_registered() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert {
        "/file/upload",
        "/file/download/{file_id}",
        "/config/list",
        "/config/value/{config_key}",
        "/notice/list",
        "/job/list",
        "/job/{job_id}/run",
    } <= paths
