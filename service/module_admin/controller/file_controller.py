"""文件上传、下载和删除接口。"""

from fastapi import APIRouter, Depends, File, Path, Request, UploadFile

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.file_dto import (
    FileChunkCompleteDto,
    FileChunkInitDto,
    FilePresignedUrlDto,
    FileUploadResultDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.file_service import FileService


class FileController:
    """安全文件存储接口。"""

    file = APIRouter(prefix="/file", tags=["文件管理"])

    @file.post(
        "/chunk/init",
        summary="初始化分片上传",
        dependencies=[Depends(Auth.has_permission("system:file:upload"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def init_chunk(data: FileChunkInitDto, request: Request):
        """创建分片上传会话。"""
        return await FileService.init_chunk_upload(data, request)

    @file.put(
        "/chunk/{upload_id}/{chunk_index}",
        summary="上传文件分片",
        dependencies=[Depends(Auth.has_permission("system:file:upload"))],
        responses={200: {"model": ApiResponseDto[dict]}},
    )
    async def upload_chunk(
        request: Request,
        upload: UploadFile = File(..., description="文件分片"),
        upload_id: str = Path(min_length=36, max_length=36, description="上传会话"),
        chunk_index: int = Path(ge=0, description="分片序号"),
    ):
        """保存一个文件分片。"""
        return await FileService.upload_chunk(upload_id, chunk_index, upload, request)

    @file.post(
        "/chunk/complete",
        summary="完成分片上传",
        dependencies=[Depends(Auth.has_permission("system:file:upload"))],
        responses={200: {"model": ApiResponseDto[FileUploadResultDto]}},
    )
    async def complete_chunk(data: FileChunkCompleteDto, request: Request):
        """合并分片并完成文件安全检查。"""
        metadata = await FileService.complete_chunk_upload(data.upload_id, request)
        return {
            **metadata.model_dump(),
            "download_url": f"/file/download/{metadata.file_id}",
        }

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
        """上传文件并返回可用于下载的文件元数据。"""
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
        """读取文件元数据并返回文件流响应。"""
        metadata = await FileService.get_metadata(file_id, request)
        return await FileService.download(metadata, request)

    @file.get(
        "/presign/{file_id}",
        summary="生成文件临时访问地址",
        dependencies=[Depends(Auth.has_permission("system:file:download"))],
        responses={200: {"model": ApiResponseDto[FilePresignedUrlDto]}},
    )
    async def presign(
        request: Request,
        file_id: str = Path(min_length=36, max_length=36, description="文件标识"),
    ):
        """生成限定时间的文件访问地址。"""
        metadata = await FileService.get_metadata(file_id, request)
        url = await FileService.presign(metadata, request)
        return {
            "url": url,
            "expires_in": FileService._settings(request).FILE_PRESIGN_TTL_SECONDS,
        }

    @file.get(
        "/redacted/{file_id}",
        summary="下载脱敏文件",
        dependencies=[Depends(Auth.has_permission("system:file:download"))],
        response_model=None,
    )
    async def redacted_download(
        request: Request,
        file_id: str = Path(min_length=36, max_length=36, description="文件标识"),
    ):
        """返回不修改原文件的敏感字段脱敏副本。"""
        metadata = await FileService.get_metadata(file_id, request)
        return await FileService.redacted_download(metadata, request)

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
        """读取文件元数据并删除文件及其数据库记录。"""
        metadata = await FileService.get_metadata(file_id, request)
        await FileService.delete(metadata, request)
