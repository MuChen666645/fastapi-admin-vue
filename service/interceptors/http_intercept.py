"""HTTP异常拦截."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from jwt import PyJWTError
from loguru import logger
from sqlalchemy.exc import IntegrityError




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

    @staticmethod
    async def all_jwt_error(request: Request, exc: PyJWTError):
        """JWT error."""
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        )

    @staticmethod
    async def all_verify(request: Request, exc: RequestValidationError):
        """Verify."""
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        )

    @staticmethod
    async def sql_Integrity(request: Request, exc: IntegrityError):
        """将数据库完整性错误转换为客户端错误。"""
        logger.opt(
            exception=(type(exc), exc, exc.__traceback__)
        ).error(
            "Database integrity error: {} {}",
            request.method,
            request.url.path,
        )
        raise HTTPException(
            status_code=400,
            detail="database anomaly",
        )
