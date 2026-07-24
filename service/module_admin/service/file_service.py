"""本地文件和阿里云 OSS 存储服务。"""

import asyncio
import hashlib
import json
import re
import shutil
import time
import uuid
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote

import oss2
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from loguru import logger
from sqlmodel import select

from config.env import PROJECT_ROOT, Settings, settings
from module_admin.dao.tenant_scope import require_tenant_id
from module_admin.entity.do.file_do import FileChunkUploadDo, FileMetadataDo
from module_admin.service.file_security_service import FileSecurityService
from utils.time_utils import now_utc8_naive


class FileService:
    """校验、保存、读取和删除上传文件。"""

    # 文件名清洗规则和流式读写块大小是文件安全与内存占用的基础约束。
    _SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
    _CHUNK_SIZE = 1024 * 1024

    @staticmethod
    def _register_pending_storage(request: Request, metadata: FileMetadataDo) -> None:
        """登记请求事务中的对象，数据库回滚时由会话依赖补偿删除。"""
        pending = getattr(request.state, "pending_storage_objects", None)
        if pending is None:
            pending = []
            request.state.pending_storage_objects = pending
        pending.append((metadata, FileService._settings(request)))

    @staticmethod
    def _register_pending_chunk(
        request: Request, upload_id: str, app_settings: Settings
    ) -> None:
        """登记分片目录，数据库回滚时立即清理未提交的临时目录。"""
        pending = getattr(request.state, "pending_chunk_dirs", None)
        if pending is None:
            pending = []
            request.state.pending_chunk_dirs = pending
        pending.append((upload_id, app_settings))

    @classmethod
    async def cleanup_expired_chunks(
        cls, session_factory, app_settings: Settings
    ) -> int:
        """清理过期分片记录及孤立的临时文件目录。"""
        root = Path(app_settings.FILE_UPLOAD_DIR)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        root = root.resolve()
        chunk_root = root / ".chunks"
        cutoff = now_utc8_naive() - timedelta(
            seconds=app_settings.FILE_CHUNK_TTL_SECONDS
        )
        cutoff_epoch = time.time() - app_settings.FILE_CHUNK_TTL_SECONDS
        removed = 0
        async with session_factory() as session:
            result = await session.execute(
                select(FileChunkUploadDo).where(FileChunkUploadDo.updated_at < cutoff)
            )
            for item in result.scalars().all():
                shutil.rmtree(chunk_root / item.upload_id, ignore_errors=True)
                await session.delete(item)
                removed += 1
            if removed:
                await session.commit()

        if chunk_root.is_dir():
            for candidate in chunk_root.iterdir():
                if (
                    candidate.is_dir()
                    and not candidate.is_symlink()
                    and candidate.name != ".pending"
                    and candidate.stat().st_mtime < cutoff_epoch
                ):
                    shutil.rmtree(candidate, ignore_errors=True)
                    removed += 1
        pending_root = chunk_root / ".pending"
        if pending_root.is_dir():
            async with session_factory() as session:
                for manifest_path in pending_root.glob("*.json"):
                    try:
                        payload = json.loads(
                            manifest_path.read_text(encoding="utf-8")
                        )
                        storage_key = str(payload["storage_key"])
                        storage_backend = str(payload["storage_backend"])
                    except (OSError, TypeError, ValueError, json.JSONDecodeError):
                        if manifest_path.stat().st_mtime < cutoff_epoch:
                            manifest_path.unlink(missing_ok=True)
                            removed += 1
                        continue
                    metadata_result = await session.execute(
                        select(FileMetadataDo.file_id).where(
                            FileMetadataDo.storage_key == storage_key
                        )
                    )
                    metadata_exists = metadata_result.scalars().first() is not None
                    expired = (
                        manifest_path.stat().st_mtime < cutoff_epoch
                    )
                    if metadata_exists or expired:
                        if not metadata_exists:
                            await cls._delete_storage_key(
                                storage_key, storage_backend, app_settings
                            )
                        manifest_path.unlink(missing_ok=True)
                        removed += 1
        return removed

    @staticmethod
    def _settings(request: Request) -> Settings:
        """优先读取应用实例配置，兼容默认配置实例。"""
        return getattr(request.app.state, "settings", settings)

    @staticmethod
    def _original_name(upload: UploadFile) -> str:
        """提取并限制原始文件名，避免将客户端路径写入存储。"""
        name = Path(upload.filename or "").name
        if not name or name in {".", ".."}:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        return name[:255]

    @classmethod
    def _storage_key(
        cls, file_id: str, original_name: str, app_settings: Settings
    ) -> str:
        """按日期生成稳定且不包含用户输入路径的存储键。"""
        extension = Path(original_name).suffix.lower()
        prefix = app_settings.OSS_PREFIX.strip("/") or "uploads"
        date_prefix = now_utc8_naive().strftime("%Y/%m/%d")
        return f"{prefix}/{date_prefix}/{file_id}{extension}"

    @classmethod
    def _validate_extension(cls, original_name: str, app_settings: Settings) -> None:
        """校验文件扩展名是否在配置允许的范围内。"""
        extension = Path(original_name).suffix.lower()
        allowed = {
            item if item.startswith(".") else f".{item}"
            for item in app_settings.FILE_ALLOWED_EXTENSIONS
        }
        if extension not in allowed:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

    @staticmethod
    def _local_path(storage_key: str, app_settings: Settings) -> Path:
        """解析本地存储路径并阻止路径穿越。"""
        root = Path(app_settings.FILE_UPLOAD_DIR)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        root = root.resolve()
        target = (root / storage_key).resolve()
        if target != root and root not in target.parents:
            raise HTTPException(status_code=400, detail="存储路径无效")
        return target

    @classmethod
    def _chunk_dir(cls, upload_id: str, app_settings: Settings) -> Path:
        """返回位于上传根目录内的分片临时目录。"""
        root = Path(app_settings.FILE_UPLOAD_DIR)
        if not root.is_absolute():
            root = PROJECT_ROOT / root
        root = root.resolve()
        target = (root / ".chunks" / upload_id).resolve()
        if root not in target.parents:
            raise HTTPException(status_code=400, detail="分片路径无效")
        return target

    @classmethod
    def _pending_manifest_path(cls, upload_id: str, app_settings: Settings) -> Path:
        """返回合并阶段存储对象的崩溃恢复 manifest 路径。"""
        chunk_dir = cls._chunk_dir(upload_id, app_settings)
        return chunk_dir.parent / ".pending" / f"{upload_id}.json"

    @classmethod
    def _write_pending_manifest(
        cls,
        upload_id: str,
        storage_key: str,
        storage_backend: str,
        app_settings: Settings,
    ) -> None:
        """在写入最终对象前持久化存储键，覆盖进程崩溃窗口。"""
        manifest_path = cls._pending_manifest_path(upload_id, app_settings)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = manifest_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(
                {
                    "storage_key": storage_key,
                    "storage_backend": storage_backend,
                },
                separators=(",", ":"),
            ),
            encoding="utf-8",
        )
        temporary_path.replace(manifest_path)

    @classmethod
    async def init_chunk_upload(cls, data, request: Request) -> dict:
        """创建分片上传会话。"""
        app_settings = cls._settings(request)
        original_name = Path(data.filename).name
        if not original_name or original_name in {".", ".."}:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        cls._validate_extension(original_name, app_settings)
        if data.total_size > app_settings.FILE_MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="文件大小超过限制")
        upload_id = str(uuid.uuid4())
        chunk_dir = cls._chunk_dir(upload_id, app_settings)
        chunk_dir.mkdir(parents=True, exist_ok=False)
        try:
            request.state.mysql.add(
                FileChunkUploadDo(
                    upload_id=upload_id,
                    tenant_id=require_tenant_id(request),
                    created_by=getattr(request.state, "user_id", None),
                    original_name=original_name[:255],
                    content_type=data.content_type,
                    total_size=data.total_size,
                    total_chunks=data.total_chunks,
                )
            )
            cls._register_pending_chunk(request, upload_id, app_settings)
        except Exception:
            shutil.rmtree(chunk_dir, ignore_errors=True)
            raise
        return {"upload_id": upload_id, "total_chunks": data.total_chunks}

    @classmethod
    async def upload_chunk(
        cls, upload_id: str, chunk_index: int, upload: UploadFile, request: Request
    ) -> dict:
        """保存一个上传分片并更新幂等接收记录。"""
        app_settings = cls._settings(request)
        session = request.state.mysql
        item = await session.get(FileChunkUploadDo, upload_id)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = require_tenant_id(request)
        if (
            item is None
            or item.tenant_id != tenant_id
            or (item.created_by is not None and item.created_by != user_id)
        ):
            raise HTTPException(status_code=404, detail="分片上传会话不存在")
        if chunk_index < 0 or chunk_index >= item.total_chunks:
            raise HTTPException(status_code=422, detail="分片序号无效")
        chunk_dir = cls._chunk_dir(upload_id, app_settings)
        chunk_path = chunk_dir / f"{chunk_index}.part"
        size = 0
        with chunk_path.open("wb") as destination:
            while True:
                chunk = await upload.read(cls._CHUNK_SIZE)
                if not chunk:
                    break
                size += len(chunk)
                if size > cls._CHUNK_SIZE:
                    chunk_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="分片大小超过限制")
                destination.write(chunk)
        received = set(json.loads(item.received_chunks_json or "[]"))
        received.add(chunk_index)
        item.received_chunks_json = json.dumps(sorted(received))
        item.updated_at = now_utc8_naive()
        return {
            "upload_id": upload_id,
            "chunk_index": chunk_index,
            "received": len(received),
        }

    @classmethod
    async def complete_chunk_upload(
        cls, upload_id: str, request: Request
    ) -> FileMetadataDo:
        """校验所有分片、执行内容安全检查并生成文件元数据。"""
        app_settings = cls._settings(request)
        session = request.state.mysql
        item = await session.get(FileChunkUploadDo, upload_id)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = require_tenant_id(request)
        if (
            item is None
            or item.tenant_id != tenant_id
            or (item.created_by is not None and item.created_by != user_id)
        ):
            raise HTTPException(status_code=404, detail="分片上传会话不存在")
        received = set(json.loads(item.received_chunks_json or "[]"))
        expected = set(range(item.total_chunks))
        if received != expected:
            raise HTTPException(status_code=409, detail="分片尚未全部上传")

        chunk_dir = cls._chunk_dir(upload_id, app_settings)
        assembled_path = chunk_dir / "assembled"
        total_size = 0
        checksum = hashlib.sha256()
        sample = bytearray()
        content = bytearray()
        with assembled_path.open("wb") as destination:
            for index in range(item.total_chunks):
                chunk = (chunk_dir / f"{index}.part").read_bytes()
                total_size += len(chunk)
                checksum.update(chunk)
                if len(sample) < 32:
                    sample.extend(chunk[: 32 - len(sample)])
                destination.write(chunk)
                content.extend(chunk)
        if total_size != item.total_size:
            raise HTTPException(status_code=409, detail="文件总大小校验失败")
        FileSecurityService.validate_signature(
            item.original_name,
            bytes(sample),
            item.content_type,
            app_settings,
        )
        if app_settings.FILE_STORAGE_BACKEND == "local":
            file_id = str(uuid.uuid4())
            storage_key = cls._storage_key(file_id, item.original_name, app_settings)
            cls._write_pending_manifest(
                upload_id,
                storage_key,
                app_settings.FILE_STORAGE_BACKEND,
                app_settings,
            )
            target = cls._local_path(storage_key, app_settings)
            target.parent.mkdir(parents=True, exist_ok=True)
            await FileSecurityService.scan_path(assembled_path, app_settings)
            shutil.move(str(assembled_path), str(target))
        else:
            await FileSecurityService.scan_bytes(bytes(content), app_settings)
            file_id = str(uuid.uuid4())
            storage_key = cls._storage_key(file_id, item.original_name, app_settings)
            cls._write_pending_manifest(
                upload_id,
                storage_key,
                app_settings.FILE_STORAGE_BACKEND,
                app_settings,
            )
            bucket = cls._oss_bucket(app_settings)
            await asyncio.to_thread(bucket.put_object, storage_key, bytes(content))
        metadata = FileMetadataDo(
            file_id=file_id,
            tenant_id=item.tenant_id,
            original_name=item.original_name,
            storage_key=storage_key,
            storage_backend=app_settings.FILE_STORAGE_BACKEND,
            content_type=item.content_type,
            file_size=total_size,
            checksum=checksum.hexdigest(),
            created_by=item.created_by,
        )
        cls._register_pending_storage(request, metadata)
        session.add(metadata)
        await session.delete(item)
        shutil.rmtree(chunk_dir, ignore_errors=True)
        return metadata

    @staticmethod
    def _oss_bucket(app_settings: Settings):
        """创建 OSS 存储桶客户端。"""
        if not app_settings.OSS_ENDPOINT or not app_settings.OSS_BUCKET:
            raise HTTPException(status_code=503, detail="OSS 存储未配置")
        auth = oss2.Auth(app_settings.ACCESS_KEY_ID, app_settings.ACCESSKEY_SECRET)
        return oss2.Bucket(auth, app_settings.OSS_ENDPOINT, app_settings.OSS_BUCKET)

    @classmethod
    async def upload(
        cls,
        upload: UploadFile,
        request: Request,
    ) -> FileMetadataDo:
        """流式保存文件并记录元数据。"""
        app_settings = cls._settings(request)
        original_name = cls._original_name(upload)
        cls._validate_extension(original_name, app_settings)
        file_id = str(uuid.uuid4())
        storage_key = cls._storage_key(file_id, original_name, app_settings)
        checksum = hashlib.sha256()
        total_size = 0
        local_path: Path | None = None
        content = bytearray()
        sample = bytearray()

        if upload.size and upload.size > app_settings.FILE_MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="文件大小超过限制")

        try:
            if app_settings.FILE_STORAGE_BACKEND == "local":
                local_path = cls._local_path(storage_key, app_settings)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                with local_path.open("wb") as destination:
                    while True:
                        chunk = await upload.read(cls._CHUNK_SIZE)
                        if not chunk:
                            break
                        total_size += len(chunk)
                        if total_size > app_settings.FILE_MAX_SIZE_BYTES:
                            raise HTTPException(
                                status_code=413, detail="文件大小超过限制"
                            )
                        checksum.update(chunk)
                        if len(sample) < 32:
                            sample.extend(chunk[: 32 - len(sample)])
                        destination.write(chunk)
            else:
                while True:
                    chunk = await upload.read(cls._CHUNK_SIZE)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > app_settings.FILE_MAX_SIZE_BYTES:
                        raise HTTPException(status_code=413, detail="文件大小超过限制")
                    checksum.update(chunk)
                    if len(sample) < 32:
                        sample.extend(chunk[: 32 - len(sample)])
                    content.extend(chunk)
                FileSecurityService.validate_signature(
                    original_name,
                    bytes(sample),
                    upload.content_type,
                    app_settings,
                )
                await FileSecurityService.scan_bytes(bytes(content), app_settings)
                bucket = cls._oss_bucket(app_settings)
                await asyncio.to_thread(bucket.put_object, storage_key, bytes(content))
            if app_settings.FILE_STORAGE_BACKEND == "local":
                FileSecurityService.validate_signature(
                    original_name,
                    bytes(sample),
                    upload.content_type,
                    app_settings,
                )
                await FileSecurityService.scan_path(local_path, app_settings)
        except Exception:
            if local_path is not None:
                local_path.unlink(missing_ok=True)
            elif app_settings.FILE_STORAGE_BACKEND != "local":
                try:
                    await cls._delete_storage_key(
                        storage_key, app_settings.FILE_STORAGE_BACKEND, app_settings
                    )
                except Exception:
                    logger.exception(
                        "文件上传失败后的对象清理失败", storage_key=storage_key
                    )
            raise

        metadata = FileMetadataDo(
            file_id=file_id,
            tenant_id=require_tenant_id(request),
            original_name=original_name,
            storage_key=storage_key,
            storage_backend=app_settings.FILE_STORAGE_BACKEND,
            content_type=upload.content_type,
            file_size=total_size,
            checksum=checksum.hexdigest(),
            created_by=getattr(request.state, "user_id", None),
        )
        cls._register_pending_storage(request, metadata)
        request.state.mysql.add(metadata)
        return metadata

    @classmethod
    async def store_bytes(
        cls,
        original_name: str,
        content: bytes,
        tenant_id: int,
        created_by: int,
        session,
        app_settings: Settings,
        content_type: str,
    ) -> FileMetadataDo:
        """将服务端生成的文件写入统一存储并登记元数据。"""
        original_name = Path(original_name).name
        cls._validate_extension(original_name, app_settings)
        if len(content) > app_settings.FILE_MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="文件大小超过限制")
        await FileSecurityService.scan_bytes(content, app_settings)
        file_id = str(uuid.uuid4())
        storage_key = cls._storage_key(file_id, original_name, app_settings)
        try:
            if app_settings.FILE_STORAGE_BACKEND == "local":
                target = cls._local_path(storage_key, app_settings)
                target.parent.mkdir(parents=True, exist_ok=True)
                await asyncio.to_thread(target.write_bytes, content)
            else:
                bucket = cls._oss_bucket(app_settings)
                await asyncio.to_thread(bucket.put_object, storage_key, content)
            metadata = FileMetadataDo(
                file_id=file_id,
                tenant_id=tenant_id,
                original_name=original_name,
                storage_key=storage_key,
                storage_backend=app_settings.FILE_STORAGE_BACKEND,
                content_type=content_type,
                file_size=len(content),
                checksum=hashlib.sha256(content).hexdigest(),
                created_by=created_by,
            )
            session.add(metadata)
            return metadata
        except Exception:
            await cls._delete_storage_key(
                storage_key, app_settings.FILE_STORAGE_BACKEND, app_settings
            )
            raise

    @classmethod
    async def get_metadata(cls, file_id: str, request: Request) -> FileMetadataDo:
        """根据文件标识查询元数据。"""
        try:
            parsed_id = str(uuid.UUID(file_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="文件不存在") from exc
        metadata = await request.state.mysql.get(FileMetadataDo, parsed_id)
        tenant_id = require_tenant_id(request)
        if metadata is None or metadata.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="文件不存在")
        return metadata

    @classmethod
    async def download(cls, metadata: FileMetadataDo, request: Request):
        """从配置的存储后端读取文件内容。"""
        app_settings = cls._settings(request)
        if metadata.storage_backend == "local":
            path = cls._local_path(metadata.storage_key, app_settings)
            if not path.is_file():
                raise HTTPException(status_code=404, detail="文件内容不存在")
            return FileResponse(
                path,
                media_type=metadata.content_type or "application/octet-stream",
                filename=metadata.original_name,
            )

        bucket = cls._oss_bucket(app_settings)
        try:
            result = await asyncio.to_thread(bucket.get_object, metadata.storage_key)
            content = await asyncio.to_thread(result.read)
        except Exception as exc:
            logger.exception("OSS 文件下载失败")
            raise HTTPException(status_code=404, detail="文件内容不存在") from exc
        return Response(
            content=content,
            media_type=metadata.content_type or "application/octet-stream",
            headers={
                "Content-Disposition": (
                    "attachment; filename*=UTF-8''" f"{quote(metadata.original_name)}"
                )
            },
        )

    @classmethod
    async def presign(cls, metadata: FileMetadataDo, request: Request) -> str:
        """生成 OSS 临时下载地址，或返回本地受保护下载接口。"""
        app_settings = cls._settings(request)
        if metadata.storage_backend == "local":
            return f"/file/download/{metadata.file_id}"
        bucket = cls._oss_bucket(app_settings)
        return await asyncio.to_thread(
            bucket.sign_url,
            "GET",
            metadata.storage_key,
            app_settings.FILE_PRESIGN_TTL_SECONDS,
        )

    @classmethod
    async def redacted_download(cls, metadata: FileMetadataDo, request: Request):
        """以脱敏副本形式返回文本文件，不改写原始文件。"""
        extension = Path(metadata.original_name).suffix.lower()
        if extension not in {".txt", ".csv", ".json"}:
            raise HTTPException(status_code=415, detail="仅支持文本文件脱敏")
        app_settings = cls._settings(request)
        if metadata.storage_backend == "local":
            path = cls._local_path(metadata.storage_key, app_settings)
            if not path.is_file():
                raise HTTPException(status_code=404, detail="文件内容不存在")
            content = await asyncio.to_thread(path.read_bytes)
        else:
            bucket = cls._oss_bucket(app_settings)
            result = await asyncio.to_thread(bucket.get_object, metadata.storage_key)
            content = await asyncio.to_thread(result.read)
        redacted = FileSecurityService.redact_text(content, app_settings)
        return Response(
            content=redacted,
            media_type=metadata.content_type or "text/plain",
            headers={
                "Content-Disposition": (
                    "attachment; filename*=UTF-8''"
                    f"{quote(Path(metadata.original_name).stem + '-redacted' + extension)}"
                )
            },
        )

    @classmethod
    async def delete(cls, metadata: FileMetadataDo, request: Request) -> None:
        """删除文件内容及对应的元数据。"""
        app_settings = cls._settings(request)
        await cls.delete_stored_file(metadata, app_settings)
        await request.state.mysql.delete(metadata)

    @classmethod
    async def delete_stored_file(
        cls, metadata: FileMetadataDo, app_settings: Settings
    ) -> None:
        """删除存储后端中的文件内容，不触碰数据库元数据。"""
        await cls._delete_storage_key(
            metadata.storage_key, metadata.storage_backend, app_settings
        )

    @classmethod
    async def _delete_storage_key(
        cls, storage_key: str, storage_backend: str, app_settings: Settings
    ) -> None:
        """删除指定存储对象；补偿清理要求本地和 OSS 行为一致。"""
        if storage_backend == "local":
            cls._local_path(storage_key, app_settings).unlink(missing_ok=True)
        else:
            bucket = cls._oss_bucket(app_settings)
            await asyncio.to_thread(bucket.delete_object, storage_key)
