"""本地文件和阿里云 OSS 存储服务。"""

import asyncio
import hashlib
import re
import uuid
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import oss2
from fastapi import HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, Response
from loguru import logger

from config.env import PROJECT_ROOT, Settings, settings
from module_admin.entity.do.file_do import FileMetadataDo


class FileService:
    """校验、保存、读取和删除上传文件。"""

    _SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
    _CHUNK_SIZE = 1024 * 1024

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
    def _storage_key(cls, file_id: str, original_name: str, app_settings: Settings) -> str:
        """按日期生成稳定且不包含用户输入路径的存储键。"""
        extension = Path(original_name).suffix.lower()
        prefix = app_settings.OSS_PREFIX.strip("/") or "uploads"
        date_prefix = datetime.now().strftime("%Y/%m/%d")
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
                            raise HTTPException(status_code=413, detail="文件大小超过限制")
                        checksum.update(chunk)
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
                    content.extend(chunk)
                bucket = cls._oss_bucket(app_settings)
                await asyncio.to_thread(bucket.put_object, storage_key, bytes(content))
        except Exception:
            if local_path is not None:
                local_path.unlink(missing_ok=True)
            raise

        metadata = FileMetadataDo(
            file_id=file_id,
            original_name=original_name,
            storage_key=storage_key,
            storage_backend=app_settings.FILE_STORAGE_BACKEND,
            content_type=upload.content_type,
            file_size=total_size,
            checksum=checksum.hexdigest(),
            created_by=getattr(request.state, "user_id", None),
        )
        request.state.mysql.add(metadata)
        return metadata

    @classmethod
    async def get_metadata(cls, file_id: str, request: Request) -> FileMetadataDo:
        """根据文件标识查询元数据。"""
        try:
            parsed_id = str(uuid.UUID(file_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="文件不存在") from exc
        metadata = await request.state.mysql.get(FileMetadataDo, parsed_id)
        if metadata is None:
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
                    "attachment; filename*=UTF-8''"
                    f"{quote(metadata.original_name)}"
                )
            },
        )

    @classmethod
    async def delete(cls, metadata: FileMetadataDo, request: Request) -> None:
        """删除文件内容及对应的元数据。"""
        app_settings = cls._settings(request)
        if metadata.storage_backend == "local":
            cls._local_path(metadata.storage_key, app_settings).unlink(missing_ok=True)
        else:
            bucket = cls._oss_bucket(app_settings)
            await asyncio.to_thread(bucket.delete_object, metadata.storage_key)
        await request.state.mysql.delete(metadata)
