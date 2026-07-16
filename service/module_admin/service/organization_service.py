"""部门和岗位业务层。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from module_admin.dao.organization_dao import OrganizationDao
from module_admin.entity.do.organization_do import DepartmentDo, PostDo
from utils.fastapi_admin import FastApiAdmin


def _raise_if_error(result: str | None) -> None:
    """将数据访问层的业务错误转换为 HTTP 异常。"""
    if result is not None:
        status_code = 404 if result.endswith("不存在") else 400
        raise HTTPException(status_code=status_code, detail=result)


class DepartmentService:
    """部门业务服务。"""

    @staticmethod
    async def list(request: Request, name: str | None, status: str | None):
        items = await OrganizationDao.list_departments(request, name, status)
        return FastApiAdmin.create_three(items, "dept_id", "parent_id")

    @staticmethod
    async def detail(dept_id: int, request: Request):
        item = await OrganizationDao.get_by_id(DepartmentDo, dept_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="部门不存在")
        return item

    @staticmethod
    async def create(data, request: Request):
        _raise_if_error(await OrganizationDao.create_department(data, request))

    @staticmethod
    async def update(dept_id: int, data, request: Request):
        _raise_if_error(await OrganizationDao.update_department(dept_id, data, request))

    @staticmethod
    async def delete(dept_id: int, request: Request):
        _raise_if_error(await OrganizationDao.delete_department(dept_id, request))


class PostService:
    """岗位业务服务。"""

    @staticmethod
    async def list(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        return await OrganizationDao.list_posts(request, name, status, params)

    @staticmethod
    async def detail(post_id: int, request: Request):
        item = await OrganizationDao.get_by_id(PostDo, post_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="岗位不存在")
        return item

    @staticmethod
    async def create(data, request: Request):
        _raise_if_error(await OrganizationDao.create_post(data, request))

    @staticmethod
    async def update(post_id: int, data, request: Request):
        _raise_if_error(await OrganizationDao.update_post(post_id, data, request))

    @staticmethod
    async def delete(post_id: int, request: Request):
        _raise_if_error(await OrganizationDao.delete_post(post_id, request))
