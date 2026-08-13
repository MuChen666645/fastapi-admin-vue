# 后端项目事实

## 运行环境

- `service/` 是基于 FastAPI、SQLModel、MySQL、Redis、Alembic、Poetry 和
  Python 3.11 的异步服务。
- `config.env.Settings` 加载 development、staging 或 production 环境配置；运行
  凭据只允许存在于环境配置。
- 管理 API 位于 `settings.API_V1_PREFIX`，当前为 `/api/v1`，并使用统一响应拦截器。

## 源码目录

| 位置 | 职责 |
| --- | --- |
| `module_admin/controller/` | HTTP 路由、依赖、请求绑定、响应声明 |
| `module_admin/service/` | 业务规则、事务编排、领域校验 |
| `module_admin/dao/` | SQLModel 持久化和查询构建 |
| `module_admin/entity/do/` | 持久化模型 |
| `module_admin/entity/dto/` | 请求与响应 DTO |
| `middleware/`、`interceptors/` | HTTP、可观测性、幂等和响应等横切能力 |
| `config/` | 类型化环境、数据库、Redis 和限流配置 |
| `alembic/` | 版本化数据库迁移链 |
| `scripts/` | 显式运维命令，例如数据库迁移 |
| `test/` | 契约、安全、迁移、生命周期和回归测试 |

## 应用生命周期

`main.create_app()` 创建隔离的应用实例。生命周期建立 Redis 和 MySQL，执行权限同步，
启动清理与导出 Worker，按配置启动调度器，并按相反顺序释放资源。测试通过应用工厂注入
依赖与任务处理器，避免修改模块全局状态。

## 数据库版本

- Alembic 当前迁移头为 `0028_tenant_and_system_parameter_menus`。
- `Settings.DATABASE_SCHEMA_VERSION` 必须等于迁移头，并由
  `test/test_migration_config.py` 校验。
- `alembic/versions/` 是部署升级历史。不得将已应用版本作为日常清理对象删除、改名、
  压缩或重写；修复通过新增版本完成，并保留 MySQL DDL 重试安全。

## 命令

| 命令 | 用途 |
| --- | --- |
| `poetry run python -m pytest -q` | 完整本地测试集 |
| `poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test` | 语法与导入编译 |
| `poetry run alembic upgrade head --sql` | 离线迁移 SQL 校验 |
| `poetry run python scripts/migrate_database.py` | 对选定数据库应用已核验迁移 |

本地测试受继承环境影响时，设置 `APP_ENV=development` 和 `DEBUG=true`。
