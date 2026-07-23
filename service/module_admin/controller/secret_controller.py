"""密钥轮换运维接口。"""

from fastapi import APIRouter, Depends, Request

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.system_config_service import SystemConfigService


class SecretController:
    """提供受保护的敏感配置轮换操作。"""

    secret = APIRouter(prefix="/ops/secrets", tags=["密钥管理"])

    @secret.post(
        "/rotate",
        summary="轮换敏感配置密钥",
        dependencies=[Depends(Auth.has_permission("system:secret:rotate"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def rotate(request: Request):
        """将当前租户敏感配置重新加密。"""
        count = await SystemConfigService.rotate_secrets(request)
        return {"rotated": count}
