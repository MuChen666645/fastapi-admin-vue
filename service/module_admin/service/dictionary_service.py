"""字典模块业务层。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from module_admin.dao.dictionary_dao import DictionaryDao
from module_admin.entity.do.dictionary_do import DictDataDo, DictTypeDo


def _raise_if_error(result: str | None) -> None:
    """将 DAO 业务错误消息转换为合适的 HTTP 异常。"""
    if result is not None:
        status_code = 404 if result.endswith("不存在") else 400
        raise HTTPException(status_code=status_code, detail=result)


class DictionaryService:
    """字典类型和字典数据业务服务。"""

    @staticmethod
    async def list_types(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        """分页返回字典类型列表。"""
        return await DictionaryDao.list_types(request, name, status, params)

    @staticmethod
    async def type_detail(dict_id: int, request: Request):
        """返回一个字典类型，不存在时抛出 404 异常。"""
        item = await DictionaryDao.get_by_id(DictTypeDo, dict_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="字典类型不存在")
        return item

    @staticmethod
    async def create_type(data, request: Request):
        """完成 DAO 校验后创建字典类型。"""
        _raise_if_error(await DictionaryDao.create_type(data, request))

    @staticmethod
    async def update_type(dict_id: int, data, request: Request):
        """修改字典类型及其关联数据引用。"""
        _raise_if_error(await DictionaryDao.update_type(dict_id, data, request))

    @staticmethod
    async def delete_type(dict_id: int, request: Request):
        """仅在没有字典数据时删除字典类型。"""
        _raise_if_error(await DictionaryDao.delete_type(dict_id, request))

    @staticmethod
    async def list_data(
        request: Request, dict_type: str | None, status: str | None, params: Params
    ):
        """按可选类型和状态分页返回字典数据。"""
        return await DictionaryDao.list_data(request, dict_type, status, params)

    @staticmethod
    async def data_detail(dict_code: int, request: Request):
        """返回一条字典数据，不存在时抛出 404 异常。"""
        item = await DictionaryDao.get_by_id(DictDataDo, dict_code, request)
        if item is None:
            raise HTTPException(status_code=404, detail="字典数据不存在")
        return item

    @staticmethod
    async def create_data(data, request: Request):
        """在已有字典类型下创建一条字典数据。"""
        _raise_if_error(await DictionaryDao.create_data(data, request))

    @staticmethod
    async def update_data(dict_code: int, data, request: Request):
        """修改字典数据并保持字典类型引用完整。"""
        _raise_if_error(await DictionaryDao.update_data(dict_code, data, request))

    @staticmethod
    async def delete_data(dict_code: int, request: Request):
        """删除一条字典数据。"""
        _raise_if_error(await DictionaryDao.delete_data(dict_code, request))
