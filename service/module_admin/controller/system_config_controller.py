"""系统参数配置接口。"""

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.entity.dto.system_config_dto import (
    SystemConfigCreateDto,
    SystemConfigDto,
    SystemConfigUpdateDto,
    SystemConfigValueDto,
)
from module_admin.service.system_config_service import SystemConfigService


class SystemConfigController:
    """系统参数配置接口。"""

    config = APIRouter(prefix="/config", tags=["系统参数"])

    @config.get(
        "/list",
        summary="分页查询系统参数",
        dependencies=[Depends(Auth.has_permission("system:config:list"))],
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[SystemConfigDto]]}},
    )
    async def list_configs(
        request: Request,
        name: str | None = Query(default=None, description="参数名称，支持模糊查询"),
        key: str | None = Query(default=None, description="参数键名，支持模糊查询"),
        params: Params = Depends(),
    ):
        return await SystemConfigService.list_configs(request, name, key, params)

    @config.get(
        "/value/{config_key}",
        summary="查询系统参数值",
        dependencies=[Depends(Auth.has_permission("system:config:query"))],
        responses={200: {"model": ApiResponseDto[SystemConfigValueDto]}},
    )
    async def value(
        request: Request,
        config_key: str = Path(description="参数键名"),
    ):
        return await SystemConfigService.value(config_key, request)

    @config.get(
        "/{config_id}",
        summary="查询系统参数详情",
        dependencies=[Depends(Auth.has_permission("system:config:query"))],
        responses={200: {"model": ApiResponseDto[SystemConfigDto]}},
    )
    async def detail(
        request: Request,
        config_id: int = Path(description="参数编号"),
    ):
        return await SystemConfigService.detail(config_id, request)

    @config.post(
        "/add",
        summary="新增系统参数",
        dependencies=[Depends(Auth.has_permission("system:config:add"))],
        responses={200: {"model": ApiResponseDto[SystemConfigDto]}},
    )
    async def create(data: SystemConfigCreateDto, request: Request):
        return await SystemConfigService.create(data, request)

    @config.put(
        "/{config_id}",
        summary="修改系统参数",
        dependencies=[Depends(Auth.has_permission("system:config:edit"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update(
        data: SystemConfigUpdateDto,
        request: Request,
        config_id: int = Path(description="参数编号"),
    ):
        return await SystemConfigService.update(config_id, data, request)

    @config.delete(
        "/{config_id}",
        summary="删除系统参数",
        dependencies=[Depends(Auth.has_permission("system:config:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        config_id: int = Path(description="参数编号"),
    ):
        return await SystemConfigService.delete(config_id, request)
