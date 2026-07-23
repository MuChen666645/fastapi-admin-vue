"""日志管理请求和响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LogQueryDto(BaseModel):
    """日志查询条件。"""

    username: str | None = Field(
        default=None, description="用户名，支持模糊查询", title="用户名"
    )
    status: str | None = Field(
        default=None,
        pattern="^[01]$",
        description="登录状态：0失败，1成功",
        title="登录状态",
    )
    path: str | None = Field(
        default=None, description="请求路径，支持模糊查询", title="请求路径"
    )
    start_time: datetime | None = Field(
        default=None, description="查询开始时间", title="查询开始时间"
    )
    end_time: datetime | None = Field(
        default=None, description="查询结束时间", title="查询结束时间"
    )


class LoginLogDto(BaseModel):
    """登录日志响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="登录日志ID", title="登录日志ID")
    user_id: int | None = Field(default=None, description="用户ID", title="用户ID")
    username: str = Field(description="登录用户名或手机号", title="登录用户名")
    ip_address: str | None = Field(
        default=None, description="客户端IP地址", title="客户端IP地址"
    )
    user_agent: str | None = Field(
        default=None, description="客户端User-Agent", title="客户端User-Agent"
    )
    status: str = Field(description="登录状态：0失败，1成功", title="登录状态")
    message: str | None = Field(
        default=None, description="登录结果说明", title="登录结果说明"
    )
    login_time: datetime = Field(description="登录时间", title="登录时间")


class OperationLogDto(BaseModel):
    """操作日志响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="操作日志ID", title="操作日志ID")
    user_id: int | None = Field(
        default=None, description="操作用户ID", title="操作用户ID"
    )
    username: str | None = Field(
        default=None, description="操作用户名", title="操作用户名"
    )
    method: str = Field(description="HTTP请求方法", title="HTTP请求方法")
    path: str = Field(description="请求路径", title="请求路径")
    ip_address: str | None = Field(
        default=None, description="客户端IP地址", title="客户端IP地址"
    )
    user_agent: str | None = Field(
        default=None, description="客户端User-Agent", title="客户端User-Agent"
    )
    status_code: int = Field(description="HTTP响应状态码", title="HTTP响应状态码")
    duration_ms: int = Field(description="请求耗时，单位毫秒", title="请求耗时")
    operation_time: datetime = Field(description="操作时间", title="操作时间")


class ExceptionLogDto(BaseModel):
    """异常日志响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="异常日志ID", title="异常日志ID")
    user_id: int | None = Field(
        default=None, description="操作用户ID", title="操作用户ID"
    )
    username: str | None = Field(
        default=None, description="操作用户名", title="操作用户名"
    )
    method: str = Field(description="HTTP请求方法", title="HTTP请求方法")
    path: str = Field(description="请求路径", title="请求路径")
    ip_address: str | None = Field(
        default=None, description="客户端IP地址", title="客户端IP地址"
    )
    exception_type: str = Field(description="异常类型", title="异常类型")
    exception_message: str = Field(description="异常信息", title="异常信息")
    traceback: str | None = Field(
        default=None, description="异常堆栈", title="异常堆栈"
    )
    exception_time: datetime = Field(description="异常发生时间", title="异常发生时间")


class BatchLogIdsDto(BaseModel):
    """批量删除日志请求模型。"""

    ids: list[int] = Field(min_length=1, description="待删除的日志ID列表")


class OnlineSessionDto(BaseModel):
    """在线会话响应，不包含原始 JWT。"""

    token_id: str = Field(
        description="Token会话ID，不包含原始Token", title="Token会话ID"
    )
    user_id: int | str = Field(description="用户ID", title="用户ID")
    username: str | None = Field(default=None, description="用户名", title="用户名")
    ip_address: str | None = Field(
        default=None, description="登录IP地址", title="登录IP地址"
    )
    user_agent: str | None = Field(
        default=None, description="客户端User-Agent", title="客户端User-Agent"
    )
    login_time: datetime | None = Field(
        default=None, description="登录时间", title="登录时间"
    )
    expire_time: datetime = Field(description="Token过期时间", title="Token过期时间")


class OnlineQueryDto(BaseModel):
    """在线用户查询条件。"""

    username: str | None = Field(
        default=None, description="用户名，支持模糊查询", title="用户名"
    )
    ip_address: str | None = Field(
        default=None, description="登录IP，支持模糊查询", title="登录IP"
    )


class ForceLogoutUserResultDto(BaseModel):
    """强制用户下线操作的结果模型。"""

    user_id: int = Field(description="被强制下线的用户ID", title="被强制下线的用户ID")
    revoked_token_count: int = Field(
        ge=0, description="已撤销的Token数量", title="已撤销的Token数量"
    )
