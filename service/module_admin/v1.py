""" This module contains the API endpoints for the admin module. """

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware
from config.env import settings
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


class AdminAPI:
    """This class contains the API endpoints for the admin module."""

    def __init__(self, app: FastAPI, *args, **kwargs) -> None:
        """初始化APP."""
        super().__init__(*args, **kwargs)
        if app is not None:
            self.init_router(app)
            # CORS配置
            app.add_middleware(
                CORSMiddleware,
                allow_origins=settings.ORIGINS,
                allow_credentials=settings.CREDENTIALS,
                allow_methods=settings.MEDOTHS,
                allow_headers=settings.HEADERS,
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
