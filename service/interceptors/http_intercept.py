"""HTTP异常拦截."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from jwt import PyJWTError
from loguru import logger
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

from middleware.response_intercept import SKIP_RESPONSE_WRAPPER_HEADER
from module_admin.error_codes import default_error_code


class ApiExceptionInterception:
    """HTTP异常拦截器."""

    def __init__(self, app: FastAPI, *args, **kwargs) -> None:
        """初始化APP."""
        super().__init__(*args, **kwargs)
        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI):
        """初始化APP.

        Args:
            app (FastAPI): APP.
        """
        app.add_exception_handler(RequestValidationError, handler=self.all_verify)
        app.add_exception_handler(PyJWTError, handler=self.all_jwt_error)
        app.add_exception_handler(IntegrityError, handler=self.sql_Integrity)
        app.add_exception_handler(Exception, handler=self.all_exception)

    @staticmethod
    async def all_jwt_error(request: Request, exc: PyJWTError):
        """统一处理 JWT 校验异常。"""
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )

    @staticmethod
    async def all_verify(request: Request, exc: RequestValidationError):
        """统一处理请求参数校验异常。"""
        raise HTTPException(
            status_code=422,
            detail=jsonable_encoder(exc.errors()),
        )

    @staticmethod
    async def sql_Integrity(request: Request, exc: IntegrityError):
        """将数据库完整性错误转换为客户端错误。"""
        logger.opt(exception=(type(exc), exc, exc.__traceback__)).error(
            "Database integrity error: {} {}",
            request.method,
            request.url.path,
        )
        raise HTTPException(
            status_code=400,
            detail="database anomaly",
        )

    @staticmethod
    async def all_exception(request: Request, exc: Exception) -> JSONResponse:
        """记录未知异常，并返回对外统一的脱敏 500 响应。"""
        logger.opt(exception=(type(exc), exc, exc.__traceback__)).error(
            "Unhandled application error: {} {}",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "error_code": default_error_code(500),
                "message": "Internal Server Error",
                "data": None,
            },
            headers={SKIP_RESPONSE_WRAPPER_HEADER: "1"},
        )
