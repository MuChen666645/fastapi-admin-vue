"""数据库备份和恢复接口。"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.backup_service import BackupService


class BackupRestoreDto(BaseModel):
    """备份文件名。"""

    filename: str = Field(min_length=1, max_length=255, description="备份文件名")


class BackupController:
    """提供受权限保护的数据库备份恢复操作。"""

    backup = APIRouter(prefix="/ops/backup", tags=["数据库备份"])

    @backup.post(
        "/create",
        summary="创建数据库备份",
        dependencies=[Depends(Auth.has_permission("system:backup:create"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def create(request: Request):
        """创建加密数据库备份并应用保留策略。"""
        app_settings = getattr(request.app.state, "settings", settings)
        path = await BackupService.create_backup(app_settings)
        return {"filename": path.name}

    @backup.post(
        "/restore",
        summary="恢复数据库备份",
        dependencies=[Depends(Auth.has_permission("system:backup:restore"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def restore(data: BackupRestoreDto, request: Request):
        """仅从配置备份目录恢复加密备份。"""
        app_settings = getattr(request.app.state, "settings", settings)
        await BackupService.restore_backup(data.filename, app_settings)
