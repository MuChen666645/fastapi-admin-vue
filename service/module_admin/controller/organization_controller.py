"""部门和岗位控制器。"""

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi_pagination import Page, Params

from module_admin.auth.authorization import Auth
from module_admin.entity.dto.organization_dto import (
    DepartmentCreateDto,
    DepartmentDto,
    DepartmentUpdateDto,
    PostCreateDto,
    PostDto,
    PostUpdateDto,
)
from module_admin.entity.dto.response_dto import ApiResponseDto
from module_admin.service.organization_service import DepartmentService, PostService


def permission(code: str):
    """生成模块权限依赖。"""
    return [Depends(Auth.has_permission(code))]


class DepartmentController:
    """部门接口。"""

    dept = APIRouter(prefix="/dept", tags=["部门模块"])

    @dept.get(
        "/list",
        summary="查询部门列表",
        dependencies=permission("system:dept:list"),
        responses={200: {"model": ApiResponseDto[list[DepartmentDto]]}},
    )
    async def list_departments(
        request: Request,
        name: str = Query(default=None, description="部门名称"),
        status: str = Query(default=None, pattern="^[01]$", description="部门状态"),
    ):
        """查询部门树。"""
        return await DepartmentService.list(request, name, status)

    @dept.get(
        "/{dept_id}",
        summary="查询部门详情",
        dependencies=permission("system:dept:query"),
        responses={200: {"model": ApiResponseDto[DepartmentDto]}},
    )
    async def get_department(
        request: Request, dept_id: int = Path(description="部门ID")
    ):
        """查询部门详情。"""
        return await DepartmentService.detail(dept_id, request)

    @dept.post(
        "/add",
        summary="新增部门",
        dependencies=permission("system:dept:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_department(data: DepartmentCreateDto, request: Request):
        """新增部门。"""
        return await DepartmentService.create(data, request)

    @dept.put(
        "/{dept_id}",
        summary="修改部门",
        dependencies=permission("system:dept:edit"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_department(
        data: DepartmentUpdateDto,
        request: Request,
        dept_id: int = Path(description="部门ID"),
    ):
        """修改部门。"""
        return await DepartmentService.update(dept_id, data, request)

    @dept.delete(
        "/{dept_id}",
        summary="删除部门",
        dependencies=permission("system:dept:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_department(
        request: Request, dept_id: int = Path(description="部门ID")
    ):
        """删除部门。"""
        return await DepartmentService.delete(dept_id, request)


class PostController:
    """岗位接口。"""

    post = APIRouter(prefix="/post", tags=["岗位模块"])

    @post.get(
        "/list",
        summary="查询岗位列表",
        dependencies=permission("system:post:list"),
        response_model=None,
        responses={200: {"model": ApiResponseDto[Page[PostDto]]}},
    )
    async def list_posts(
        request: Request,
        name: str = Query(default=None, description="岗位名称"),
        status: str = Query(default=None, pattern="^[01]$", description="岗位状态"),
        params: Params = Depends(),
    ):
        """分页查询岗位。"""
        return await PostService.list(request, name, status, params)

    @post.get(
        "/{post_id}",
        summary="查询岗位详情",
        dependencies=permission("system:post:query"),
        responses={200: {"model": ApiResponseDto[PostDto]}},
    )
    async def get_post(request: Request, post_id: int = Path(description="岗位ID")):
        """查询岗位详情。"""
        return await PostService.detail(post_id, request)

    @post.post(
        "/add",
        summary="新增岗位",
        dependencies=permission("system:post:add"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def create_post(data: PostCreateDto, request: Request):
        """新增岗位。"""
        return await PostService.create(data, request)

    @post.put(
        "/{post_id}",
        summary="修改岗位",
        dependencies=permission("system:post:edit"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def update_post(
        data: PostUpdateDto,
        request: Request,
        post_id: int = Path(description="岗位ID"),
    ):
        """修改岗位。"""
        return await PostService.update(post_id, data, request)

    @post.delete(
        "/{post_id}",
        summary="删除岗位",
        dependencies=permission("system:post:remove"),
        responses={200: {"model": ApiResponseDto[None]}},
    )
    async def delete_post(request: Request, post_id: int = Path(description="岗位ID")):
        """删除岗位。"""
        return await PostService.delete(post_id, request)
