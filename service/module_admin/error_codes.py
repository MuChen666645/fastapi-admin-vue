"""统一 API 错误码。"""

ERROR_CODE_BY_STATUS = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def default_error_code(status_code: int) -> str:
    """将 HTTP 状态映射为稳定错误码。"""
    return ERROR_CODE_BY_STATUS.get(status_code, f"HTTP_{status_code}")
