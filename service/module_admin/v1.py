"""后台管理模块的 API 路由注册入口。"""

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from config.env import Settings, settings
from config.mysql_serve import bind_request_mysql_session
from module_admin.controller.backup_controller import BackupController
from module_admin.controller.code_controller import CodeController
from module_admin.controller.dictionary_controller import DictionaryController
from module_admin.controller.external_auth_controller import ExternalAuthController
from module_admin.controller.file_controller import FileController
from module_admin.controller.health_controller import HealthController
from module_admin.controller.job_controller import JobController
from module_admin.controller.log_controller import LogController
from module_admin.controller.menu_contorller import MenuController
from module_admin.controller.notice_controller import NoticeController
from module_admin.controller.organization_controller import (
    DepartmentController,
    PostController,
)
from module_admin.controller.role_controller import RoleController
from module_admin.controller.secret_controller import SecretController
from module_admin.controller.system_config_controller import SystemConfigController
from module_admin.controller.tenant_controller import TenantController
from module_admin.controller.user_controller import UserController


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
        app_settings = getattr(app.state, "settings", settings)
        version_prefix = app_settings.API_V1_PREFIX.rstrip("/")

        def include(router, dependencies=None):
            app.include_router(
                router,
                prefix=version_prefix,
                dependencies=dependencies or [],
            )

        include(HealthController.health)
        include(ExternalAuthController.auth, db_dependencies)
        include(BackupController.backup, db_dependencies)
        include(UserController(app).user, db_dependencies)
        include(CodeController(app).code)
        include(RoleController(app).role, db_dependencies)
        include(MenuController(app).menu, db_dependencies)
        include(DepartmentController.dept, db_dependencies)
        include(PostController.post, db_dependencies)
        include(DictionaryController.dictionary, db_dependencies)
        include(LogController.log, db_dependencies)
        include(LogController.online, db_dependencies)
        include(FileController.file, db_dependencies)
        include(SystemConfigController.config, db_dependencies)
        include(SecretController.secret, db_dependencies)
        include(NoticeController.notice, db_dependencies)
        include(JobController.job, db_dependencies)
        include(TenantController.tenant, db_dependencies)
