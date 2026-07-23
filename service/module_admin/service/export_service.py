"""持久化异步导出任务服务。"""

import asyncio
import uuid
from dataclasses import dataclass
from datetime import timedelta

from fastapi import HTTPException, Request
from loguru import logger
from sqlmodel import select

from config.env import Settings, settings
from module_admin.dao.tenant_scope import require_tenant_id
from module_admin.entity.do.export_do import ExportTaskDo
from module_admin.entity.do.file_do import FileMetadataDo
from module_admin.service.excel_service import ExcelService
from module_admin.service.file_service import FileService
from utils.time_utils import now_utc8_naive


@dataclass(frozen=True)
class ExportTaskRef:
    """任务领取后脱离数据库会话使用的最小任务信息。"""

    task_id: str
    tenant_id: int
    created_by: int
    resource: str


class ExportService:
    """创建、领取、执行和查询异步导出任务。"""

    CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    RESOURCES = {"users", "roles", "dictionary"}

    @staticmethod
    def _settings(request: Request) -> Settings:
        return getattr(request.app.state, "settings", settings)

    @classmethod
    async def create(cls, resource: str, request: Request) -> dict[str, object]:
        """创建任务并在返回前提交，使后台轮询器可以立即领取。"""
        if resource not in cls.RESOURCES:
            raise HTTPException(status_code=422, detail="不支持的导出资源")
        actor_user_id = getattr(request.state, "user_id", None)
        if actor_user_id is None:
            raise HTTPException(status_code=401, detail="未授权")
        app_settings = cls._settings(request)
        task = ExportTaskDo(
            id=str(uuid.uuid4()),
            tenant_id=require_tenant_id(request),
            created_by=int(actor_user_id),
            resource=resource,
            expires_at=now_utc8_naive()
            + timedelta(seconds=app_settings.EXPORT_TASK_TTL_SECONDS),
        )
        request.state.mysql.add(task)
        await request.state.mysql.commit()
        return {"task_id": task.id, "resource": resource, "status": task.status}

    @classmethod
    async def get_task(cls, task_id: str, request: Request) -> dict[str, object]:
        """只返回当前租户且由当前用户创建的任务。"""
        task = await cls._get_owned_task(task_id, request)
        if task.expires_at <= now_utc8_naive():
            raise HTTPException(status_code=404, detail="导出任务已过期")
        return {
            "task_id": task.id,
            "resource": task.resource,
            "status": task.status,
            "file_id": task.file_id if task.status == "success" else None,
            "error": task.error_message if task.status == "failed" else None,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "finished_at": task.finished_at,
            "expires_at": task.expires_at,
        }

    @classmethod
    async def get_download(cls, task_id: str, request: Request):
        """返回已完成任务的文件，并再次执行文件租户校验。"""
        task = await cls._get_owned_task(task_id, request)
        if task.expires_at <= now_utc8_naive() or task.status != "success":
            raise HTTPException(status_code=409, detail="导出任务尚未完成")
        if not task.file_id:
            raise HTTPException(status_code=404, detail="导出文件不存在")
        metadata = await FileService.get_metadata(task.file_id, request)
        return await FileService.download(metadata, request)

    @classmethod
    async def _get_owned_task(cls, task_id: str, request: Request) -> ExportTaskDo:
        actor_user_id = getattr(request.state, "user_id", None)
        tenant_id = require_tenant_id(request)
        task = await request.state.mysql.get(ExportTaskDo, task_id)
        if (
            task is None
            or task.tenant_id != tenant_id
            or task.created_by != actor_user_id
        ):
            raise HTTPException(status_code=404, detail="导出任务不存在")
        return task

    @classmethod
    async def worker_loop(cls, session_factory, app_settings: Settings) -> None:
        """轮询并执行持久化任务，进程重启后可继续领取未完成任务。"""
        if not app_settings.EXPORT_WORKER_ENABLED:
            return
        while True:
            try:
                task = await cls._claim_one(session_factory)
                if task is None:
                    await cls._cleanup_expired(session_factory, app_settings)
                    await asyncio.sleep(app_settings.EXPORT_POLL_SECONDS)
                    continue
                await cls._execute(task, session_factory, app_settings)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(app_settings.EXPORT_POLL_SECONDS)

    @staticmethod
    async def _claim_one(session_factory) -> ExportTaskRef | None:
        async with session_factory() as session:
            result = await session.execute(
                select(ExportTaskDo)
                .where(
                    ExportTaskDo.status == "pending",
                    ExportTaskDo.expires_at > now_utc8_naive(),
                )
                .order_by(ExportTaskDo.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            task = result.scalars().first()
            if task is None:
                return None
            task.status = "running"
            task.started_at = now_utc8_naive()
            await session.commit()
            return ExportTaskRef(
                task.id, task.tenant_id, task.created_by, task.resource
            )

    @classmethod
    async def _execute(
        cls, task_ref: ExportTaskRef, session_factory, app_settings: Settings
    ) -> None:
        async with session_factory() as session:
            task = await session.get(ExportTaskDo, task_ref.task_id)
            if task is None or task.status != "running":
                return
            metadata = None
            try:
                filename, headers, rows = await ExcelService.build_export(
                    task.resource,
                    session,
                    task.tenant_id,
                    task.created_by,
                )
                metadata = await FileService.store_bytes(
                    filename,
                    ExcelService._workbook_bytes(headers, rows),
                    task.tenant_id,
                    task.created_by,
                    session,
                    app_settings,
                    cls.CONTENT_TYPE,
                )
                task.file_id = metadata.file_id
                task.status = "success"
                task.finished_at = now_utc8_naive()
                task.error_message = None
                await session.commit()
            except Exception as exc:
                try:
                    await session.rollback()
                except Exception:
                    logger.exception("异步导出失败后的数据库回滚失败")
                if metadata is not None:
                    try:
                        await FileService.delete_stored_file(metadata, app_settings)
                    except Exception:
                        logger.exception(
                            "异步导出数据库回滚后的文件补偿清理失败",
                            storage_key=metadata.storage_key,
                        )
                failed = await session.get(ExportTaskDo, task_ref.task_id)
                if failed is not None:
                    failed.status = "failed"
                    failed.finished_at = now_utc8_naive()
                    failed.error_message = str(exc)[:2000]
                    await session.commit()

    @staticmethod
    async def _cleanup_expired(session_factory, app_settings: Settings) -> None:
        async with session_factory() as session:
            result = await session.execute(
                select(ExportTaskDo)
                .where(ExportTaskDo.expires_at <= now_utc8_naive())
                .limit(50)
                .with_for_update(skip_locked=True)
            )
            tasks = list(result.scalars().all())
            for task in tasks:
                if task.file_id:
                    metadata = await session.get(FileMetadataDo, task.file_id)
                    if metadata is not None:
                        await FileService.delete_stored_file(metadata, app_settings)
                        await session.delete(metadata)
                await session.delete(task)
            if tasks:
                await session.commit()
