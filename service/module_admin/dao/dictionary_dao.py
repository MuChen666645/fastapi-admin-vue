"""字典模块数据访问层。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.dictionary_do import DictDataDo, DictTypeDo
from utils.time_utils import now_utc8_naive


class DictionaryDao:
    """字典类型和字典数据数据库操作。"""

    @staticmethod
    async def get_by_id(model, item_id: int, request: Request):
        return await request.state.mysql.get(model, item_id)

    @staticmethod
    async def list_types(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        query = select(DictTypeDo).order_by(DictTypeDo.dict_id)
        if name:
            query = query.where(DictTypeDo.dict_name.contains(name))
        if status is not None:
            query = query.where(DictTypeDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def create_type(data, request: Request):
        request.state.mysql.add(DictTypeDo(**data.model_dump()))

    @staticmethod
    async def update_type(dict_id: int, data, request: Request):
        mysql = request.state.mysql
        item = await mysql.get(DictTypeDo, dict_id)
        if item is None:
            return "字典类型不存在"
        values = data.model_dump(exclude_unset=True)
        old_type = item.dict_type
        new_type = values.get("dict_type")
        values["update_time"] = now_utc8_naive()
        item.sqlmodel_update(values)
        # 类型编码是字典数据的关联键，修改时必须同步更新。
        if new_type and new_type != old_type:
            result = await mysql.execute(
                select(DictDataDo).where(DictDataDo.dict_type == old_type)
            )
            for dict_data in result.scalars().all():
                dict_data.dict_type = new_type
                dict_data.update_time = now_utc8_naive()
        return None

    @staticmethod
    async def delete_type(dict_id: int, request: Request):
        mysql = request.state.mysql
        item = await mysql.get(DictTypeDo, dict_id)
        if item is None:
            return "字典类型不存在"
        result = await mysql.execute(
            select(DictDataDo.dict_code)
            .where(DictDataDo.dict_type == item.dict_type)
            .limit(1)
        )
        if result.scalars().first() is not None:
            return "字典类型存在字典数据，不能删除"
        await mysql.delete(item)
        return None

    @staticmethod
    async def list_data(
        request: Request, dict_type: str | None, status: str | None, params: Params
    ):
        query = select(DictDataDo).order_by(DictDataDo.dict_sort, DictDataDo.dict_code)
        if dict_type:
            query = query.where(DictDataDo.dict_type == dict_type)
        if status is not None:
            query = query.where(DictDataDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def create_data(data, request: Request):
        mysql = request.state.mysql
        result = await mysql.execute(
            select(DictTypeDo.dict_id).where(DictTypeDo.dict_type == data.dict_type)
        )
        if result.scalars().first() is None:
            return "字典类型不存在"
        mysql.add(DictDataDo(**data.model_dump()))
        return None

    @staticmethod
    async def update_data(dict_code: int, data, request: Request):
        mysql = request.state.mysql
        item = await mysql.get(DictDataDo, dict_code)
        if item is None:
            return "字典数据不存在"
        values = data.model_dump(exclude_unset=True)
        new_type = values.get("dict_type")
        if new_type:
            result = await mysql.execute(
                select(DictTypeDo.dict_id).where(DictTypeDo.dict_type == new_type)
            )
            if result.scalars().first() is None:
                return "字典类型不存在"
        values["update_time"] = now_utc8_naive()
        item.sqlmodel_update(values)
        return None

    @staticmethod
    async def delete_data(dict_code: int, request: Request):
        mysql = request.state.mysql
        item = await mysql.get(DictDataDo, dict_code)
        if item is None:
            return "字典数据不存在"
        await mysql.delete(item)
        return None
