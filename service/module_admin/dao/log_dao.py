"""Log data access layer."""

from fastapi import Request
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlmodel import delete, select

from module_admin.entity.do.log_do import ExceptionLogDo, LoginLogDo, OperationLogDo
from module_admin.service.data_scope_service import DataScopeService


class LogDao:
    """Persist and query system logs."""

    @staticmethod
    async def create(model, request: Request) -> None:
        session_factory = getattr(request.app.state, "mysql_session_factory", None)
        if session_factory is None:
            return
        async with session_factory() as mysql:
            mysql.add(model)
            try:
                await mysql.commit()
            except Exception:
                await mysql.rollback()
                raise

    @staticmethod
    async def list_logs(model, query, params, request: Request, time_field: str):
        filters = []
        if query.username and hasattr(model, "username"):
            filters.append(model.username.contains(query.username))
        if query.status is not None and hasattr(model, "status"):
            filters.append(model.status == query.status)
        if query.path and hasattr(model, "path"):
            filters.append(model.path.contains(query.path))
        time_column = getattr(model, time_field)
        if query.start_time:
            filters.append(time_column >= query.start_time)
        if query.end_time:
            filters.append(time_column <= query.end_time)

        mysql = request.state.mysql
        scope = await DataScopeService.resolve(request)
        filters.append(scope.user_id_clause(model.user_id))
        query = select(model).where(*filters).order_by(time_column.desc())
        return await paginate(mysql, query, params=params)

    @staticmethod
    async def delete_logs(model, ids: list[int], request: Request) -> None:
        mysql = request.state.mysql
        scope = await DataScopeService.resolve(request)
        await mysql.execute(
            delete(model).where(
                model.id.in_(set(ids)),
                scope.user_id_clause(model.user_id),
            )
        )

    @staticmethod
    async def create_login(log: LoginLogDo, request: Request) -> None:
        await LogDao.create(log, request)

    @staticmethod
    async def create_operation(log: OperationLogDo, request: Request) -> None:
        await LogDao.create(log, request)

    @staticmethod
    async def create_exception(log: ExceptionLogDo, request: Request) -> None:
        await LogDao.create(log, request)
