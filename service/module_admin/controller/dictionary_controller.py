"""字典模块控制器。"""

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.dictionary_dto import (
    DictDataCreateDto,
    DictDataDto,
    DictDataUpdateDto,
    DictTypeCreateDto,
    DictTypeDto,
    DictTypeUpdateDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.dictionary_service import DictionaryService


def permission(code: str):
    return [Depends(Auth.has_permission(code))]


class DictionaryController:
    """字典类型和字典数据接口。"""

    dictionary = APIRouter(prefix="/dict", tags=["字典模块"])

    @dictionary.get(
        "/type/list",
        summary="查询字典类型列表",
        dependencies=permission("system:dict:list"),
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[DictTypeDto]]}},
    )
    async def list_types(
        request: Request,
        name: str = Query(default=None, description="字典名称"),
        status: str = Query(default=None, pattern="^[01]$", description="字典状态"),
        params: Params = Depends(),
    ):
        return await DictionaryService.list_types(request, name, status, params)

    @dictionary.get(
        "/type/{dict_id}",
        summary="查询字典类型详情",
        dependencies=permission("system:dict:query"),
        responses={200: {"model": ApiResponseDto[DictTypeDto]}},
    )
    async def get_type(request: Request, dict_id: int = Path(description="字典类型ID")):
        return await DictionaryService.type_detail(dict_id, request)

    @dictionary.post(
        "/type/add",
        summary="新增字典类型",
        dependencies=permission("system:dict:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_type(data: DictTypeCreateDto, request: Request):
        return await DictionaryService.create_type(data, request)

    @dictionary.put(
        "/type/{dict_id}",
        summary="修改字典类型",
        dependencies=permission("system:dict:edit"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_type(
        data: DictTypeUpdateDto,
        request: Request,
        dict_id: int = Path(description="字典类型ID"),
    ):
        return await DictionaryService.update_type(dict_id, data, request)

    @dictionary.delete(
        "/type/{dict_id}",
        summary="删除字典类型",
        dependencies=permission("system:dict:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_type(request: Request, dict_id: int = Path(description="字典类型ID")):
        return await DictionaryService.delete_type(dict_id, request)

    @dictionary.get(
        "/data/list",
        summary="查询字典数据列表",
        dependencies=permission("system:dict:list"),
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[DictDataDto]]}},
    )
    async def list_data(
        request: Request,
        dict_type: str = Query(default=None, description="字典类型编码"),
        status: str = Query(default=None, pattern="^[01]$", description="字典状态"),
        params: Params = Depends(),
    ):
        return await DictionaryService.list_data(request, dict_type, status, params)

    @dictionary.get(
        "/data/{dict_code}",
        summary="查询字典数据详情",
        dependencies=permission("system:dict:query"),
        responses={200: {"model": ApiResponseDto[DictDataDto]}},
    )
    async def get_data(request: Request, dict_code: int = Path(description="字典数据ID")):
        return await DictionaryService.data_detail(dict_code, request)

    @dictionary.post(
        "/data/add",
        summary="新增字典数据",
        dependencies=permission("system:dict:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_data(data: DictDataCreateDto, request: Request):
        return await DictionaryService.create_data(data, request)

    @dictionary.put(
        "/data/{dict_code}",
        summary="修改字典数据",
        dependencies=permission("system:dict:edit"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_data(
        data: DictDataUpdateDto,
        request: Request,
        dict_code: int = Path(description="字典数据ID"),
    ):
        return await DictionaryService.update_data(dict_code, data, request)

    @dictionary.delete(
        "/data/{dict_code}",
        summary="删除字典数据",
        dependencies=permission("system:dict:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_data(request: Request, dict_code: int = Path(description="字典数据ID")):
        return await DictionaryService.delete_data(dict_code, request)
