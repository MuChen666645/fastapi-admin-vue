"""字典模块业务层。"""

from fastapi import HTTPException, Request
from fastapi_pagination import Params

from module_admin.dao.dictionary_dao import DictionaryDao
from module_admin.entity.do.dictionary_do import DictDataDo, DictTypeDo


def _raise_if_error(result: str | None) -> None:
    if result is not None:
        status_code = 404 if result.endswith("不存在") else 400
        raise HTTPException(status_code=status_code, detail=result)


class DictionaryService:
    """字典类型和字典数据业务服务。"""

    @staticmethod
    async def list_types(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        return await DictionaryDao.list_types(request, name, status, params)

    @staticmethod
    async def type_detail(dict_id: int, request: Request):
        item = await DictionaryDao.get_by_id(DictTypeDo, dict_id, request)
        if item is None:
            raise HTTPException(status_code=404, detail="字典类型不存在")
        return item

    @staticmethod
    async def create_type(data, request: Request):
        _raise_if_error(await DictionaryDao.create_type(data, request))

    @staticmethod
    async def update_type(dict_id: int, data, request: Request):
        _raise_if_error(await DictionaryDao.update_type(dict_id, data, request))

    @staticmethod
    async def delete_type(dict_id: int, request: Request):
        _raise_if_error(await DictionaryDao.delete_type(dict_id, request))

    @staticmethod
    async def list_data(
        request: Request, dict_type: str | None, status: str | None, params: Params
    ):
        return await DictionaryDao.list_data(request, dict_type, status, params)

    @staticmethod
    async def data_detail(dict_code: int, request: Request):
        item = await DictionaryDao.get_by_id(DictDataDo, dict_code, request)
        if item is None:
            raise HTTPException(status_code=404, detail="字典数据不存在")
        return item

    @staticmethod
    async def create_data(data, request: Request):
        _raise_if_error(await DictionaryDao.create_data(data, request))

    @staticmethod
    async def update_data(dict_code: int, data, request: Request):
        _raise_if_error(await DictionaryDao.update_data(dict_code, data, request))

    @staticmethod
    async def delete_data(dict_code: int, request: Request):
        _raise_if_error(await DictionaryDao.delete_data(dict_code, request))
