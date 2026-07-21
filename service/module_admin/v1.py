"""后台管理模块的 API 路由注册入口。"""

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from config.env import Settings, settings
from config.mysql_serve import bind_request_mysql_session
from module_admin.controller.health_controller import HealthController
from module_admin.controller.user_controller import UserController
from module_admin.controller.code_controller import CodeController
from module_admin.controller.role_controller import RoleController
from module_admin.controller.menu_contorller import MenuController
from module_admin.controller.organization_controller import (
    DepartmentController,
    PostController,
)
from module_admin.controller.dictionary_controller import DictionaryController
from module_admin.controller.log_controller import LogController
from module_admin.controller.file_controller import FileController
from module_admin.controller.job_controller import JobController
from module_admin.controller.notice_controller import NoticeController
from module_admin.controller.system_config_controller import SystemConfigController


class AdminAPI:
    """注册后台管理模块的 API 路由和跨域中间件。"""

    def __init__(
        self,
        app: FastAPI,
        app_settings: Settings | None = None,
        *args,
        **kwargs,
    ) -> None:
        """初始化APP."""
        super().__init__(*args, **kwargs)
        if app is not None:
            self.init_router(app)
            # CORS配置
            app_settings = app_settings or settings
            app.add_middleware(
                CORSMiddleware,
                allow_origins=app_settings.ORIGINS,
                allow_credentials=app_settings.CREDENTIALS,
                allow_methods=app_settings.MEDOTHS,
                allow_headers=app_settings.HEADERS,
            )

    @staticmethod
    def init_router(app: FastAPI) -> None:
        """初始化路由."""
        db_dependencies = [Depends(bind_request_mysql_session)]
        app.include_router(HealthController.health)
        app.include_router(UserController(app).user, dependencies=db_dependencies)
        app.include_router(CodeController(app).code)
        app.include_router(RoleController(app).role, dependencies=db_dependencies)
        app.include_router(MenuController(app).menu, dependencies=db_dependencies)
        app.include_router(DepartmentController.dept, dependencies=db_dependencies)
        app.include_router(PostController.post, dependencies=db_dependencies)
        app.include_router(
            DictionaryController.dictionary, dependencies=db_dependencies
        )
        app.include_router(LogController.log, dependencies=db_dependencies)
        app.include_router(LogController.online, dependencies=db_dependencies)
        app.include_router(FileController.file, dependencies=db_dependencies)
        app.include_router(SystemConfigController.config, dependencies=db_dependencies)
        app.include_router(NoticeController.notice, dependencies=db_dependencies)
        app.include_router(JobController.job, dependencies=db_dependencies)
