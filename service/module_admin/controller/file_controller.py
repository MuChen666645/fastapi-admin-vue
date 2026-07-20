"""文件上传、下载和删除接口。"""

from fastapi import APIRouter, Depends, File, Path, Request, UploadFile

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.file_dto import FileUploadResultDto
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.file_service import FileService


class FileController:
    """安全文件存储接口。"""

    file = APIRouter(prefix="/file", tags=["文件管理"])

    @file.post(
        "/upload",
        summary="上传文件",
        dependencies=[Depends(Auth.has_permission("system:file:upload"))],
        responses={200: {"model": ApiResponseDto[FileUploadResultDto]}},
    )
    async def upload(
        request: Request,
        file: UploadFile = File(..., description="待上传的文件"),
    ):
        metadata = await FileService.upload(file, request)
        return {
            **metadata.model_dump(),
            "download_url": f"/file/download/{metadata.file_id}",
        }

    @file.get(
        "/download/{file_id}",
        summary="下载文件",
        dependencies=[Depends(Auth.has_permission("system:file:download"))],
        response_model=None,
    )
    async def download(
        request: Request,
        file_id: str = Path(
            min_length=36,
            max_length=36,
            description="文件标识",
        ),
    ):
        metadata = await FileService.get_metadata(file_id, request)
        return await FileService.download(metadata, request)

    @file.delete(
        "/{file_id}",
        summary="删除文件",
        dependencies=[Depends(Auth.has_permission("system:file:remove"))],
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete(
        request: Request,
        file_id: str = Path(
            min_length=36,
            max_length=36,
            description="文件标识",
        ),
    ):
        metadata = await FileService.get_metadata(file_id, request)
        await FileService.delete(metadata, request)
