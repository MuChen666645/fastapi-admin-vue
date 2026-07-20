"""系统参数业务服务。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from module_admin.dao.system_config_dao import SystemConfigDao


class SystemConfigService:
    """校验并协调系统参数业务操作。"""

    @staticmethod
    async def list_configs(request: Request, name: str | None, key: str | None, params: Params):
        """分页查询系统参数。"""
        return await SystemConfigDao.list_configs(request, name, key, params)

    @staticmethod
    async def detail(config_id: int, request: Request):
        """查询系统参数详情。"""
        item = await SystemConfigDao.get_by_id(config_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        return item

    @staticmethod
    async def value(config_key: str, request: Request):
        """按参数键名查询参数值。"""
        item = await SystemConfigDao.get_by_key(config_key, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        return {"config_key": item.config_key, "config_value": item.config_value}

    @staticmethod
    async def create(data, request: Request):
        """创建系统参数并校验键名唯一性。"""
        if await SystemConfigDao.get_by_key(data.config_key, request):
            raise HTTPException(status_code=409, detail="系统参数键名已存在")
        return await SystemConfigDao.create(data, request)

    @staticmethod
    async def update(config_id: int, data, request: Request):
        """更新系统参数。"""
        item = await SystemConfigService.detail(config_id, request)
        await SystemConfigDao.update(item.id, data, request)

    @staticmethod
    async def delete(config_id: int, request: Request):
        """删除非内置系统参数。"""
        item = await SystemConfigService.detail(config_id, request)
        if item.is_builtin:
            raise HTTPException(status_code=400, detail="内置系统参数不能删除")
        await SystemConfigDao.delete(item.id, request)
