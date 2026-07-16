"""入口文件."""

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from loguru import logger
from asyncio import create_task
from sqlalchemy.sql import text

# 环境配置
from config.env import settings
from config.rate_limit import limiter

# 异常拦截器
from interceptors.http_intercept import ApiExceptionInterception

# 中间件
from middleware.logger_middleware import LoggerMiddleware
from middleware.response_intercept import ResponseInterceptor

# 服务器配置
from utils.fastapi_admin import FastApiAdmin
from module_admin.v1 import AdminAPI
from config.redis_serve import RedisServe
from config.mysql_serve import MysqlServe, bind_request_mysql_session

# 服务启动
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    :param app: FastAPI实例
    """
    logger.info("服务启动中...")
    # 限制请求速率
    app.state.limiter = limiter
    app.state.redis = await RedisServe.get_redis_server()
    engine, Session = await MysqlServe.get_mysql_config()
    sql_scripts = [
        FastApiAdmin.get_file("assets/sql/schema-upgrade.sql"),
        FastApiAdmin.get_file("assets/sql/fastapi-admin.sql"),
    ]
    async with Session() as session:
        for sql_script in sql_scripts:
            await session.execute(text(sql_script))
        await session.commit()
    app.state.mysql_session_factory = Session
    FastApiAdmin.start_serve()
    logger.info("服务启动完成...")
    yield
    logger.info("正在关闭MySQL连接...")
    if engine:
        await engine.dispose()
        logger.info("MySQL连接已关闭!")
    create_task(RedisServe.close_redis_server(app))


# 创建app实例
app = FastAPI(
    debug=settings.DEBUG,
    title=settings.TITLE,
    summary=settings.SUMMARY,
    version=settings.VERSION,
    openapi_url=settings.OPENAPI_URL,
    responses=settings.RESPONSES,
    lifespan=lifespan,
    dependencies=[Depends(bind_request_mysql_session)],
)

# 限流器异常处理
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 静态资源
app.mount("/static", StaticFiles(directory="static"), name="static")

# 异常拦截
ApiExceptionInterception(app)

# 限流器中间件
app.add_middleware(SlowAPIMiddleware)

# 响应拦截
app.add_middleware(ResponseInterceptor)

# 日志中间件
app.add_middleware(LoggerMiddleware)

# 安全中间件
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.HOSTS)

# 注册分页插件
add_pagination(app)

# 挂载路由
AdminAPI(app)
