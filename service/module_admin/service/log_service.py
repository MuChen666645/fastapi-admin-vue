"""日志业务服务。"""

from fastapi import Request
from fastapi_pagination import create_page

from module_admin.auth.authorization import Auth
from module_admin.dao.log_dao import LogDao
from module_admin.entity.do.log_do import ExceptionLogDo, LoginLogDo, OperationLogDo
from module_admin.service.data_scope_service import DataScopeService


class LogService:
    """管理持久化系统日志。"""

    # 日志类型映射同时定义数据模型和排序时间字段，避免控制器直接操作模型。
    LOG_TYPES = {
        "login": (LoginLogDo, "login_time"),
        "operation": (OperationLogDo, "operation_time"),
        "exception": (ExceptionLogDo, "exception_time"),
    }

    @staticmethod
    async def list_logs(log_type: str, query, params, request: Request):
        """查询受支持的日志表，并应用数据权限过滤。"""
        model, time_field = LogService.LOG_TYPES[log_type]
        return await LogDao.list_logs(model, query, params, request, time_field)

    @staticmethod
    async def delete_logs(log_type: str, ids: list[int], request: Request) -> None:
        """在操作者数据权限范围内删除选定日志。"""
        model, _ = LogService.LOG_TYPES[log_type]
        await LogDao.delete_logs(model, ids, request)

    @staticmethod
    async def list_online_users(query, params, request: Request):
        """按用户和 IP 条件过滤在线 Token 会话并分页返回。"""
        sessions = await Auth.list_online_tokens(request)
        state = getattr(request, "state", None)
        if state is not None and getattr(state, "mysql", None) is not None:
            session_user_ids = [
                int(item["user_id"])
                for item in sessions
                if item.get("user_id") is not None
            ]
            allowed_user_ids = await DataScopeService.filter_user_ids(
                request, session_user_ids
            )
            sessions = [
                item
                for item in sessions
                if item.get("user_id") in allowed_user_ids
            ]
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
