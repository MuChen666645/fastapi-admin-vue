"""Log business services."""

from fastapi import Request
from fastapi_pagination import create_page

from module_admin.auth.authorization import Auth
from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import ExceptionLogDo, LoginLogDo, OperationLogDo


class LogService:
    """Manage persisted system logs."""

    LOG_TYPES = {
        "login": (LoginLogDo, "login_time"),
        "operation": (OperationLogDo, "operation_time"),
        "exception": (ExceptionLogDo, "exception_time"),
    }

    @staticmethod
    async def list_logs(log_type: str, query, params, request: Request):
        model, time_field = LogService.LOG_TYPES[log_type]
        return await LogDao.list_logs(model, query, params, request, time_field)

    @staticmethod
    async def delete_logs(log_type: str, ids: list[int], request: Request) -> None:
        model, _ = LogService.LOG_TYPES[log_type]
        await LogDao.delete_logs(model, ids, request)

    @staticmethod
    async def list_online_users(query, params, request: Request):
        sessions = await Auth.list_online_tokens(request)
        if query.username:
            username = query.username.lower()
            sessions = [
                item
                for item in sessions
                if username in (item.get("username") or "").lower()
            ]
        if query.ip_address:
            sessions = [
                item
                for item in sessions
                if query.ip_address in (item.get("ip_address") or "")
            ]
        raw_params = params.to_raw_params()
        items = sessions[raw_params.offset : raw_params.offset + raw_params.limit]
        return create_page(items, total=len(sessions), params=params)
