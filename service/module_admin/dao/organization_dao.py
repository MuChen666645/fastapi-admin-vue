"""部门和岗位数据访问层。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.organization_do import (DepartmentDo, PostDo,
                                                    UserPostDo)
from module_admin.entity.do.user_do import UserDo
from module_admin.service.data_scope_service import DataScopeService
from utils.time_utils import now_utc8_naive


class OrganizationDao:
    """部门和岗位数据库操作。"""

    @staticmethod
    async def get_by_id(model, item_id: int, request: Request):
        """根据主键查询部门或岗位。"""
        if model is DepartmentDo:
            if not await DataScopeService.can_access_department(item_id, request):
                return None
        elif model is PostDo:
            if not await DataScopeService.can_access_post(item_id, request):
                return None
        return await request.state.mysql.get(model, item_id)

    @staticmethod
    async def list_departments(request: Request, name: str | None, status: str | None):
        """按名称和状态查询部门。"""
        scope = await DataScopeService.resolve(request)
        query = select(DepartmentDo).where(
            scope.department_id_clause(DepartmentDo.dept_id)
        ).order_by(DepartmentDo.order_num, DepartmentDo.dept_id)
        if name:
            query = query.where(DepartmentDo.dept_name.contains(name))
        if status is not None:
            query = query.where(DepartmentDo.status == status)
        result = await request.state.mysql.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_department(data, request: Request):
        """新增部门并计算祖级路径。"""
        mysql = request.state.mysql
        values = data.model_dump()
        parent_id = values.get("parent_id") or None
        parent = None
        if parent_id:
            if (
                getattr(request.state, "user_id", None) is not None
                and not await DataScopeService.can_access_department(parent_id, request)
            ):
                return "No data permission"
            parent = await mysql.get(DepartmentDo, parent_id)
            if parent is None:
                return "父部门不存在"
        if not parent and getattr(request.state, "user_id", None) is not None:
            scope = await DataScopeService.resolve(request)
            if not scope.all_data:
                return "No data permission"
        ancestors = f"{parent.ancestors},{parent.dept_id}".strip(",") if parent else "0"
        values["parent_id"] = parent_id
        mysql.add(DepartmentDo(**values, ancestors=ancestors))
        return None

    @staticmethod
    async def update_department(dept_id: int, data, request: Request):
        """修改部门，并在移动节点时同步更新所有后代的祖级路径。"""
        mysql = request.state.mysql
        dept = await OrganizationDao.get_by_id(DepartmentDo, dept_id, request)
        if dept is None:
            return "部门不存在"
        values = data.model_dump(exclude_unset=True)
        if "parent_id" in values:
            parent_id = values["parent_id"] or None
            scope = await DataScopeService.resolve(request)
            if not scope.all_data and parent_id is None:
                return "No data permission"
            if parent_id == dept_id:
                return "上级部门不能是自身"
            parent = (
                await OrganizationDao.get_by_id(DepartmentDo, parent_id, request)
                if parent_id
                else None
            )
            if parent_id and parent is None:
                return "父部门不存在"
            if parent and str(dept_id) in parent.ancestors.split(","):
                return "上级部门不能是当前部门的子部门"

            old_prefix = f"{dept.ancestors},{dept_id}"
            new_ancestors = f"{parent.ancestors},{parent.dept_id}".strip(",") if parent else "0"
            new_prefix = f"{new_ancestors},{dept_id}"
            child_result = await mysql.execute(
                select(DepartmentDo).where(DepartmentDo.ancestors.contains(str(dept_id)))
            )
            for child in child_result.scalars().all():
                child.ancestors = child.ancestors.replace(old_prefix, new_prefix, 1)
                child.update_time = now_utc8_naive()
            values["parent_id"] = parent_id
            values["ancestors"] = new_ancestors

        values["update_time"] = now_utc8_naive()
        dept.sqlmodel_update(values)
        return None

    @staticmethod
    async def delete_department(dept_id: int, request: Request):
        """删除无子部门且未分配用户的部门。"""
        mysql = request.state.mysql
        dept = await OrganizationDao.get_by_id(DepartmentDo, dept_id, request)
        if dept is None:
            return "部门不存在"
        child_result = await mysql.execute(
            select(DepartmentDo.dept_id).where(DepartmentDo.parent_id == dept_id).limit(1)
        )
        if child_result.scalars().first() is not None:
            return "部门存在子部门，不能删除"
        user_result = await mysql.execute(
            select(UserDo.id).where(UserDo.dept_id == dept_id).limit(1)
        )
        if user_result.scalars().first() is not None:
            return "部门存在用户，不能删除"
        await mysql.delete(dept)
        return None

    @staticmethod
    async def list_posts(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        """按名称和状态查询岗位。"""
        scope = await DataScopeService.resolve(request)
        query = select(PostDo).where(
            scope.post_id_clause(PostDo.post_id)
        ).order_by(PostDo.post_sort, PostDo.post_id)
        if name:
            query = query.where(PostDo.post_name.contains(name))
        if status is not None:
            query = query.where(PostDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def create_post(data, request: Request):
        """新增岗位。"""
        mysql = request.state.mysql
        if getattr(request.state, "user_id", None) is not None:
            scope = await DataScopeService.resolve(request)
            if not scope.all_data:
                return "No data permission"
        mysql.add(PostDo(**data.model_dump()))
        return None

    @staticmethod
    async def update_post(post_id: int, data, request: Request):
        """修改岗位。"""
        mysql = request.state.mysql
        if not await DataScopeService.can_mutate_post(post_id, request):
            return "No data permission"
        post = await OrganizationDao.get_by_id(PostDo, post_id, request)
        if post is None:
            return "岗位不存在"
        values = data.model_dump(exclude_unset=True)
        values["update_time"] = now_utc8_naive()
        post.sqlmodel_update(values)
        return None

    @staticmethod
    async def delete_post(post_id: int, request: Request):
        """删除未分配用户的岗位。"""
        mysql = request.state.mysql
        if not await DataScopeService.can_mutate_post(post_id, request):
            return "No data permission"
        post = await OrganizationDao.get_by_id(PostDo, post_id, request)
        if post is None:
            return "岗位不存在"
        user_result = await mysql.execute(
            select(UserPostDo.user_id).where(UserPostDo.post_id == post_id).limit(1)
        )
        if user_result.scalars().first() is not None:
            return "岗位已分配用户，不能删除"
        await mysql.delete(post)
        return None
