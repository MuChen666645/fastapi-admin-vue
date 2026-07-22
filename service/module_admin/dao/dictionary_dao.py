"""字典模块数据访问层。"""

from fastapi import Request
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlmodel import paginate
from sqlmodel import select

from module_admin.entity.do.dictionary_do import DictDataDo, DictTypeDo
from utils.time_utils import now_utc8_naive


class DictionaryDao:
    @staticmethod
    def _tenant_id(request: Request) -> int | None:
        return getattr(request.state, "tenant_id", None)

    @staticmethod
    def _tenant_filter(model, request: Request):
        tenant_id = DictionaryDao._tenant_id(request)
        return model.tenant_id == tenant_id if tenant_id is not None else True
    """字典类型和字典数据数据库操作。"""

    @staticmethod
    async def get_by_id(model, item_id: int, request: Request):
        """按主键值查询一个字典模型。"""
        key = model.dict_id if model is DictTypeDo else model.dict_code
        result = await request.state.mysql.execute(
            select(model).where(
                key == item_id,
                DictionaryDao._tenant_filter(model, request),
            )
        )
        return result.scalars().first()

    @staticmethod
    async def list_types(
        request: Request, name: str | None, status: str | None, params: Params
    ):
        """构造并分页查询过滤后的字典类型。"""
        query = select(DictTypeDo).where(
            DictionaryDao._tenant_filter(DictTypeDo, request)
        ).order_by(DictTypeDo.dict_id)
        if name:
            query = query.where(DictTypeDo.dict_name.contains(name))
        if status is not None:
            query = query.where(DictTypeDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def create_type(data, request: Request):
        """在当前请求事务中暂存新的字典类型。"""
        request.state.mysql.add(
            DictTypeDo(**data.model_dump(), tenant_id=DictionaryDao._tenant_id(request))
        )

    @staticmethod
    async def update_type(dict_id: int, data, request: Request):
        """修改字典类型，编码变化时同步迁移关联数据。"""
        mysql = request.state.mysql
        item = await DictionaryDao.get_by_id(DictTypeDo, dict_id, request)
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
                select(DictDataDo).where(
                    DictDataDo.dict_type == old_type,
                    DictionaryDao._tenant_filter(DictDataDo, request),
                )
            )
            for dict_data in result.scalars().all():
                dict_data.dict_type = new_type
                dict_data.update_time = now_utc8_naive()
        return None

    @staticmethod
    async def delete_type(dict_id: int, request: Request):
        """仅在没有数据行引用编码时删除字典类型。"""
        mysql = request.state.mysql
        item = await DictionaryDao.get_by_id(DictTypeDo, dict_id, request)
        if item is None:
            return "字典类型不存在"
        result = await mysql.execute(
            select(DictDataDo.dict_code)
            .where(
                DictDataDo.dict_type == item.dict_type,
                DictionaryDao._tenant_filter(DictDataDo, request),
            )
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
        """构造并分页查询过滤后的字典数据。"""
        query = select(DictDataDo).where(
            DictionaryDao._tenant_filter(DictDataDo, request)
        ).order_by(DictDataDo.dict_sort, DictDataDo.dict_code)
        if dict_type:
            query = query.where(DictDataDo.dict_type == dict_type)
        if status is not None:
            query = query.where(DictDataDo.status == status)
        return await paginate(request.state.mysql, query, params=params)

    @staticmethod
    async def create_data(data, request: Request):
        """校验父级字典类型，并在当前事务中暂存字典数据。"""
        mysql = request.state.mysql
        result = await mysql.execute(
            select(DictTypeDo.dict_id).where(
                DictTypeDo.dict_type == data.dict_type,
                DictionaryDao._tenant_filter(DictTypeDo, request),
            )
        )
        if result.scalars().first() is None:
            return "字典类型不存在"
        mysql.add(
            DictDataDo(**data.model_dump(), tenant_id=DictionaryDao._tenant_id(request))
        )
        return None

    @staticmethod
    async def update_data(dict_code: int, data, request: Request):
        """修改字典数据，并校验变更后的父级字典类型。"""
        mysql = request.state.mysql
        item = await DictionaryDao.get_by_id(DictDataDo, dict_code, request)
        if item is None:
            return "字典数据不存在"
        values = data.model_dump(exclude_unset=True)
        new_type = values.get("dict_type")
        if new_type:
            result = await mysql.execute(
                select(DictTypeDo.dict_id).where(
                    DictTypeDo.dict_type == new_type,
                    DictionaryDao._tenant_filter(DictTypeDo, request),
                )
            )
            if result.scalars().first() is None:
                return "字典类型不存在"
        values["update_time"] = now_utc8_naive()
        item.sqlmodel_update(values)
        return None

    @staticmethod
    async def delete_data(dict_code: int, request: Request):
        """在当前请求事务中暂存一条字典数据的删除。"""
        mysql = request.state.mysql
        item = await DictionaryDao.get_by_id(DictDataDo, dict_code, request)
        if item is None:
            return "字典数据不存在"
        await mysql.delete(item)
        return None
