"""字典模块控制器。"""

from fastapi import APIRouter, Depends, File, Path, Query, Request, UploadFile
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
from module_admin.service.excel_service import ExcelService
from module_admin.service.export_service import ExportService


def permission(code: str):
    """创建字典接口共用的权限依赖列表。"""
    return [Depends(Auth.has_permission(code))]


class DictionaryController:
    """字典类型和字典数据接口。"""

    dictionary = APIRouter(prefix="/dict", tags=["字典模块"])

    @dictionary.get(
        "/export",
        summary="导出字典 Excel",
        dependencies=permission("system:dict:list"),
        response_model=None,
    )
    async def export_dictionary(request: Request):
        """导出当前租户字典。"""
        return await ExcelService.export_dictionary(request)

    @dictionary.post(
        "/export/async",
        summary="创建异步字典导出任务",
        dependencies=permission("system:dict:list"),
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def create_async_dictionary_export(request: Request):
        """创建持久化的字典 Excel 导出任务。"""
        return await ExportService.create("dictionary", request)

    @dictionary.get(
        "/export/tasks/{task_id}",
        summary="查询异步字典导出任务",
        dependencies=permission("system:dict:list"),
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def get_async_dictionary_export(task_id: str, request: Request):
        """查询当前用户创建的字典导出任务状态。"""
        return await ExportService.get_task(task_id, request)

    @dictionary.get(
        "/export/tasks/{task_id}/download",
        summary="下载异步字典导出文件",
        dependencies=permission("system:dict:list"),
        response_model=None,
    )
    async def download_async_dictionary_export(task_id: str, request: Request):
        """下载已完成的字典导出文件。"""
        return await ExportService.get_download(task_id, request)

    @dictionary.post(
        "/import",
        summary="导入字典 Excel",
        dependencies=permission("system:dict:add"),
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def import_dictionary(
        request: Request,
        file: UploadFile = File(..., description="字典 Excel 文件"),
    ):
        """导入字典类型及字典数据。"""
        return await ExcelService.import_dictionary(file, request)

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
        """分页查询字典类型。"""
        return await DictionaryService.list_types(request, name, status, params)

    @dictionary.get(
        "/type/{dict_id}",
        summary="查询字典类型详情",
        dependencies=permission("system:dict:query"),
        responses={200: {"model": ApiResponseDto[DictTypeDto]}},
    )
    async def get_type(request: Request, dict_id: int = Path(description="字典类型ID")):
        """查询字典类型详情。"""
        return await DictionaryService.type_detail(dict_id, request)

    @dictionary.post(
        "/type/add",
        summary="新增字典类型",
        dependencies=permission("system:dict:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_type(data: DictTypeCreateDto, request: Request):
        """新增字典类型。"""
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
        """修改字典类型。"""
        return await DictionaryService.update_type(dict_id, data, request)

    @dictionary.delete(
        "/type/{dict_id}",
        summary="删除字典类型",
        dependencies=permission("system:dict:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_type(
        request: Request, dict_id: int = Path(description="字典类型ID")
    ):
        """删除字典类型。"""
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
        """分页查询字典数据。"""
        return await DictionaryService.list_data(request, dict_type, status, params)

    @dictionary.get(
        "/data/{dict_code}",
        summary="查询字典数据详情",
        dependencies=permission("system:dict:query"),
        responses={200: {"model": ApiResponseDto[DictDataDto]}},
    )
    async def get_data(
        request: Request, dict_code: int = Path(description="字典数据ID")
    ):
        """查询字典数据详情。"""
        return await DictionaryService.data_detail(dict_code, request)

    @dictionary.post(
        "/data/add",
        summary="新增字典数据",
        dependencies=permission("system:dict:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_data(data: DictDataCreateDto, request: Request):
        """新增字典数据。"""
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
        """修改字典数据。"""
        return await DictionaryService.update_data(dict_code, data, request)

    @dictionary.delete(
        "/data/{dict_code}",
        summary="删除字典数据",
        dependencies=permission("system:dict:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_data(
        request: Request, dict_code: int = Path(description="字典数据ID")
    ):
        """删除字典数据。"""
        return await DictionaryService.delete_data(dict_code, request)
