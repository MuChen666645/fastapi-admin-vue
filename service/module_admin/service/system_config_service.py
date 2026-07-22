"""系统参数业务服务。"""

import base64
import hashlib

from cryptography.fernet import Fernet
from fastapi import HTTPException, Request
from fastapi_pagination import Params

from config.env import settings
from module_admin.dao.system_config_dao import SystemConfigDao


class SystemConfigService:
    """校验、保护并协调系统参数业务操作。"""

    SECRET_CONFIG_TYPES = frozenset({"secret", "password", "sensitive"})
    MASKED_VALUE = "********"
    ENCRYPTED_PREFIX = "enc:v1:"

    @staticmethod
    def _fernet() -> Fernet:
        """使用应用密钥派生系统参数加密密钥。"""
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        )
        return Fernet(key)

    @classmethod
    def _is_secret(cls, config_type: str | None) -> bool:
        """判断参数类型是否属于敏感值。"""
        return str(config_type or "text").strip().casefold() in cls.SECRET_CONFIG_TYPES

    @classmethod
    def _protect_value(cls, value: str | None, config_type: str | None) -> str | None:
        """对敏感参数加密存储，普通参数保持原值。"""
        if value is None or not cls._is_secret(config_type):
            return value
        if value.startswith(cls.ENCRYPTED_PREFIX):
            return value
        encrypted = cls._fernet().encrypt(value.encode("utf-8")).decode("ascii")
        return f"{cls.ENCRYPTED_PREFIX}{encrypted}"

    @classmethod
    def _safe_item(cls, item):
        """返回隐藏敏感参数值的响应副本。"""
        if not cls._is_secret(getattr(item, "config_type", None)):
            return item
        return item.model_copy(update={"config_value": cls.MASKED_VALUE})

    @classmethod
    async def list_configs(
        cls, request: Request, name: str | None, key: str | None, params: Params
    ):
        """分页查询系统参数并隐藏敏感值。"""
        page = await SystemConfigDao.list_configs(request, name, key, params)
        return page.model_copy(
            update={"items": [cls._safe_item(item) for item in page.items]}
        )

    @classmethod
    async def detail(cls, config_id: int, request: Request):
        """查询系统参数详情并隐藏敏感值。"""
        item = await SystemConfigDao.get_by_id(config_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        return cls._safe_item(item)

    @classmethod
    async def value(cls, config_key: str, request: Request):
        """按参数键名查询参数值，敏感类型只返回掩码。"""
        item = await SystemConfigDao.get_by_key(config_key, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        return {
            "config_key": item.config_key,
            "config_value": (
                cls.MASKED_VALUE
                if cls._is_secret(item.config_type)
                else item.config_value
            ),
        }

    @classmethod
    async def create(cls, data, request: Request):
        """创建系统参数并校验键名唯一性。"""
        if await SystemConfigDao.get_by_key(data.config_key, request):
            raise HTTPException(status_code=409, detail="系统参数键名已存在")
        protected = data.model_copy(
            update={
                "config_value": cls._protect_value(
                    data.config_value, data.config_type
                )
            }
        )
        item = await SystemConfigDao.create(protected, request)
        return cls._safe_item(item)

    @classmethod
    async def update(cls, config_id: int, data, request: Request):
        """更新系统参数并保护新写入的敏感值。"""
        item = await SystemConfigDao.get_by_id(config_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        values = data.model_dump(exclude_unset=True)
        config_type = values.get("config_type", item.config_type)
        if "config_value" in values:
            values["config_value"] = cls._protect_value(
                values["config_value"], config_type
            )
        elif cls._is_secret(config_type) and item.config_value:
            values["config_value"] = cls._protect_value(
                item.config_value, config_type
            )
        protected = data.model_copy(update=values)
        await SystemConfigDao.update(item.id, protected, request)

    @classmethod
    async def delete(cls, config_id: int, request: Request):
        """删除非内置系统参数。"""
        item = await SystemConfigDao.get_by_id(config_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="系统参数不存在")
        if item.is_builtin:
            raise HTTPException(status_code=400, detail="内置系统参数不能删除")
        await SystemConfigDao.delete(item.id, request)
