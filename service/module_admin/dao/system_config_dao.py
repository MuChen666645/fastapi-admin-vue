"""系统参数数据访问操作。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.system_config_do import SystemConfigDo


class SystemConfigDao:
    """持久化并查询系统参数。"""

    @staticmethod
    async def list_configs(request: Request, name: str | None, key: str | None, params: Params):
        """按名称或键名分页查询系统参数。"""
        query = select(SystemConfigDo).order_by(SystemConfigDo.id.desc())
        if name:
            query = query.where(SystemConfigDo.config_name.contains(name))
        if key:
            query = query.where(SystemConfigDo.config_key.contains(key))
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def get_by_id(config_id: int, request: Request) -> SystemConfigDo | None:
        """按编号查询系统参数。"""
        return await request.state.mysql.get(SystemConfigDo, config_id)

    @staticmethod
    async def get_by_key(config_key: str, request: Request) -> SystemConfigDo | None:
        """按键名查询系统参数。"""
        result = await request.state.mysql.execute(
            select(SystemConfigDo).where(SystemConfigDo.config_key == config_key)
        )
        return result.scalars().first()

    @staticmethod
    async def create(data, request: Request) -> SystemConfigDo:
        """创建系统参数实体。"""
        item = SystemConfigDo(**data.model_dump())
        request.state.mysql.add(item)
        return item

    @staticmethod
    async def update(config_id: int, data, request: Request) -> SystemConfigDo | None:
        """更新系统参数实体。"""
        item = await request.state.mysql.get(SystemConfigDo, config_id)
        if item is None:
            return None
        item.sqlmodel_update(data.model_dump(exclude_unset=True))
        return item

    @staticmethod
    async def delete(config_id: int, request: Request) -> SystemConfigDo | None:
        """删除系统参数实体。"""
        item = await request.state.mysql.get(SystemConfigDo, config_id)
        if item is not None:
            await request.state.mysql.delete(item)
        return item
