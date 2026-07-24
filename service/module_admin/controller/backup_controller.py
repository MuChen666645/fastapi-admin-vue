"""数据库备份和恢复接口。"""

import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

from config.env import settings
from module_admin.auth.authorization import Auth
from module_admin.entity.do.user_do import UserDo
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.backup_service import BackupService
from module_admin.service.mfa_service import MfaService


class BackupRestoreDto(BaseModel):
    """备份文件名。"""

    filename: str = Field(min_length=1, max_length=255, description="备份文件名")


class BackupRestoreRequestDto(BackupRestoreDto):
    """在线恢复请求，必须同时提供二次 MFA 验证码。"""

    mfa_code: str = Field(
        min_length=6, max_length=32, description="MFA 验证码或恢复码"
    )


class BackupController:
    """仅允许平台超级管理员执行数据库备份运维操作。"""

    backup = APIRouter(prefix="/ops/backup", tags=["数据库备份"])
    PLATFORM_BACKUP_DEPENDENCIES = [Depends(Auth.platform_admin_status)]

    @staticmethod
    async def _controlled_restore_access(
        request: Request,
        data: BackupRestoreRequestDto,
        operations_token: str | None = Header(
            default=None, alias="X-Operations-Token", description="受控运维令牌"
        ),
    ) -> None:
        """在线恢复仅允许显式开启的受控运维窗口。"""
        app_settings = getattr(request.app.state, "settings", settings)
        if not (
            app_settings.BACKUP_ONLINE_RESTORE_ENABLED
            and app_settings.BACKUP_RESTORE_MAINTENANCE_MODE
        ):
            raise HTTPException(
                status_code=503,
                detail="在线数据库恢复已禁用，请使用受控运维流程",
            )
        expected = app_settings.BACKUP_RESTORE_OPERATIONS_TOKEN.strip()
        if not expected or not operations_token or not hmac.compare_digest(
            operations_token.strip(), expected
        ):
            raise HTTPException(status_code=401, detail="缺少有效的受控运维令牌")
        user = await request.state.mysql.get(UserDo, request.state.user_id)
        if user is None or not getattr(user, "mfa_enabled", False):
            raise HTTPException(status_code=403, detail="平台管理员必须启用 MFA")
        await MfaService.verify_login(user, data.mfa_code, request)

    @backup.post(
        "/create",
        summary="创建数据库备份",
        dependencies=[
            *PLATFORM_BACKUP_DEPENDENCIES,
            Depends(Auth.has_permission("system:backup:create")),
        ],
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
        dependencies=[
            *PLATFORM_BACKUP_DEPENDENCIES,
            Depends(Auth.has_permission("system:backup:restore")),
            Depends(_controlled_restore_access),
        ],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def restore(data: BackupRestoreRequestDto, request: Request):
        """仅从受控运维窗口恢复加密备份。"""
        app_settings = getattr(request.app.state, "settings", settings)
        await BackupService.restore_backup(data.filename, app_settings)

    @backup.post(
        "/verify",
        summary="校验数据库备份",
        dependencies=[
            *PLATFORM_BACKUP_DEPENDENCIES,
            Depends(Auth.has_permission("system:backup:verify")),
        ],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def verify(data: BackupRestoreDto, request: Request):
        """解密并校验备份结构，不修改目标数据库。"""
        app_settings = getattr(request.app.state, "settings", settings)
        return await BackupService.verify_backup(data.filename, app_settings)

    @backup.post(
        "/rehearse",
        summary="执行备份恢复演练",
        dependencies=[
            *PLATFORM_BACKUP_DEPENDENCIES,
            Depends(Auth.has_permission("system:backup:rehearse")),
        ],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def rehearse(data: BackupRestoreDto, request: Request):
        """在独立临时数据库导入备份并校验迁移版本。"""
        app_settings = getattr(request.app.state, "settings", settings)
        return await BackupService.rehearse_restore(data.filename, app_settings)
